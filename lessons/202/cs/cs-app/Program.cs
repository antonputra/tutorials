using System.Diagnostics;
using cs_app;
using Npgsql;
using NpgsqlTypes;
using Prometheus;
using Metrics = Prometheus.Metrics;

var builder = WebApplication.CreateBuilder(args);

// --- Logging off for benchmark; in prod emit to async file/sink ---
builder.Logging.ClearProviders();
builder.Logging.SetMinimumLevel(LogLevel.None);

// Config (same keys)
var appConfig = new AppConfig(builder.Configuration);

// S3
builder.Services.AddSingleton(new AmazonS3Uploader(appConfig.User, appConfig.Secret, appConfig.S3Endpoint,
    appConfig.Region));

// Npgsql pool tuned for hot path
var csb = new NpgsqlConnectionStringBuilder
{
    Host = appConfig.DbHost,
    Username = appConfig.DbUser,
    Password = appConfig.DbPassword,
    Database = appConfig.DbDatabase,
    Pooling = true,
    MaxPoolSize = 256,
    MinPoolSize = 16,
    NoResetOnClose = true,
    AutoPrepareMinUsages = 2,
    MaxAutoPrepare = 32,
    Multiplexing = true
};

// Register data source as app-lifetime singleton
builder.Services.AddSingleton(_ => new NpgsqlSlimDataSourceBuilder(csb.ConnectionString).Build());

var app = builder.Build();

// Create Summary Prometheus metric to measure latency of the requests.
var summary = Metrics.CreateSummary("myapp_request_duration_seconds", "Duration of the request.",
    new SummaryConfiguration
    {
        LabelNames = ["op"],
        Objectives = [new QuantileEpsilonPair(0.9, 0.01), new QuantileEpsilonPair(0.99, 0.001)]
    });
var s3Dur = summary.WithLabels("s3");
var dbDur = summary.WithLabels("db");

app.MapMetrics();
app.MapGet("/healthz", () => Results.Ok());

// Create endpoint that returns a list of connected devices.
app.MapGet("/api/devices", () => Results.Ok(StaticData.Devices));

// Create endpoint that uploads image to S3 and writes metadata to Postgres
app.MapGet("/api/images", async (HttpContext httpContext,
    AmazonS3Uploader amazonS3,
    NpgsqlDataSource dataSource) =>
{
    var id = Interlocked.Increment(ref StaticData.Counter) - 1; // start at 0
    var image = new Image($"cs-thumbnail-{id}.png");

    // S3
    var t0 = Stopwatch.GetTimestamp();
    await amazonS3.Upload(appConfig.S3Bucket, image.ObjKey, appConfig.S3ImgPath, httpContext.RequestAborted);
    s3Dur.Observe(Stopwatch.GetElapsedTime(t0).TotalSeconds);

    // DB
    var t1 = Stopwatch.GetTimestamp();
    await using (var cmd = dataSource.CreateCommand(StaticData.ImageInsertSql))
    {
        cmd.Parameters.Add(new NpgsqlParameter<Guid> { NpgsqlDbType = NpgsqlDbType.Uuid, Value = image.ImageUuid });
        cmd.Parameters.Add(new NpgsqlParameter<string> { NpgsqlDbType = NpgsqlDbType.Text, Value = image.ObjKey });
        cmd.Parameters.Add(new NpgsqlParameter<DateTime>
            { NpgsqlDbType = NpgsqlDbType.TimestampTz, Value = image.CreatedAt });
        await cmd.ExecuteNonQueryAsync(httpContext.RequestAborted);
    }
    dbDur.Observe(Stopwatch.GetElapsedTime(t1).TotalSeconds);

    return Results.Ok();
});

app.Run();

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