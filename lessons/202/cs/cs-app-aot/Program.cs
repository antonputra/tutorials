using System.Diagnostics;
using System.Text.Json.Serialization;
using cs_app_aot;
using Npgsql;
using NpgsqlTypes;
using Prometheus;
using Metrics = Prometheus.Metrics;

var builder = WebApplication.CreateSlimBuilder(args);

// hard-off logging for benchmarks (no sinks)
builder.Logging.ClearProviders();
builder.Logging.SetMinimumLevel(LogLevel.None);

// JSON source-gen for AOT; harmless on JIT
builder.Services.ConfigureHttpJsonOptions(o =>
{
    o.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonSerializerContext.Default);
});

// config
var cfg = new AppConfig(builder.Configuration);
builder.Services.AddSingleton(cfg);

// AWS S3
builder.Services.AddSingleton(new AmazonS3Uploader(cfg.User, cfg.Secret, cfg.S3Endpoint, cfg.Region));

// Npgsql (AOT/trimming friendly)
var csb = new NpgsqlConnectionStringBuilder
{
    Host = cfg.DbHost,
    Username = cfg.DbUser,
    Password = cfg.DbPassword,
    Database = cfg.DbDatabase,
    Pooling = true,
    MaxPoolSize = 256,
    MinPoolSize = 16,
    NoResetOnClose = true,
    AutoPrepareMinUsages = 2,
    MaxAutoPrepare = 32,
    Multiplexing = true
};
builder.Services.AddSingleton(_ => new NpgsqlSlimDataSourceBuilder(csb.ConnectionString).Build());

var app = builder.Build();

// Prometheus Summary (prebind labels to skip tiny allocs)
var summary = Metrics.CreateSummary("myapp_request_duration_seconds", "Duration of the request.",
    new SummaryConfiguration
    {
        LabelNames = ["op"],
        Objectives = [new QuantileEpsilonPair(0.9, 0.01), new QuantileEpsilonPair(0.99, 0.001)]
    });
var s3Dur = summary.WithLabels("s3");
var dbDur = summary.WithLabels("db");

// endpoints
app.MapMetrics();
app.MapGet("/healthz", () => Results.Ok());
app.MapGet("/api/devices", () => Results.Ok(StaticData.Devices));

app.MapGet("/api/images",
    async (HttpContext http,
        AmazonS3Uploader s3,
        NpgsqlDataSource dataSource) =>
    {
        var id = Interlocked.Increment(ref StaticData.Counter) - 1;
        var image = new Image($"cs-thumbnail-{id}.png");

        // S3
        var t0 = Stopwatch.GetTimestamp();
        await s3.Upload(cfg.S3Bucket, image.ObjKey, cfg.S3ImgPath, http.RequestAborted);
        s3Dur.Observe(Stopwatch.GetElapsedTime(t0).TotalSeconds);

        // DB
        var t1 = Stopwatch.GetTimestamp();
        await using (var cmd = dataSource.CreateCommand(StaticData.ImageInsertSql))
        {
            cmd.Parameters.Add(new NpgsqlParameter<Guid> { NpgsqlDbType = NpgsqlDbType.Uuid, Value = image.ImageUuid });
            cmd.Parameters.Add(new NpgsqlParameter<string> { NpgsqlDbType = NpgsqlDbType.Text, Value = image.ObjKey });
            cmd.Parameters.Add(new NpgsqlParameter<DateTime>
                { NpgsqlDbType = NpgsqlDbType.TimestampTz, Value = image.CreatedAt });
            await cmd.ExecuteNonQueryAsync(http.RequestAborted);
        }

        dbDur.Observe(Stopwatch.GetElapsedTime(t1).TotalSeconds);
        return Results.Ok();
    });

app.Run();

// ---- app types ----
[JsonSerializable(typeof(Device[]))]
internal partial class AppJsonSerializerContext : JsonSerializerContext;

public sealed class AppConfig(IConfiguration config)
{
    public string? DbDatabase = config.GetValue<string>("Db:database");
    public string? DbHost = config.GetValue<string>("Db:host");
    public string? DbPassword = config.GetValue<string>("Db:password");
    public string? DbUser = config.GetValue<string>("Db:user");

    public string? Region = config.GetValue<string>("S3:region");
    public string? S3Bucket = config.GetValue<string>("S3:bucket");
    public string? S3Endpoint = config.GetValue<string>("S3:endpoint");
    public string? S3ImgPath = config.GetValue<string>("S3:imgPath");
    public string? Secret = config.GetValue<string>("S3:secret");
    public string? User = config.GetValue<string>("S3:user");
}


public sealed class Device
{
    public required string Uuid { get; init; }
    public required string Mac { get; init; }
    public required string Firmware { get; init; }
}

public readonly struct Image
{
    public string ObjKey { get; }
    public Guid ImageUuid { get; }
    public DateTime CreatedAt { get; }

    public Image(string key)
    {
        ObjKey = key;
        ImageUuid = Guid.NewGuid();
        CreatedAt = DateTime.UtcNow;
    }
}