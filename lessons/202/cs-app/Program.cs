using Prometheus;
using System.Diagnostics;
using Npgsql;
using cs_app;
using System.Text.Json.Serialization;

// Initialize the Web App
var builder = WebApplication.CreateSlimBuilder(args);

// Configure JSON source generatino for AOT support
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonSerializerContext.Default);
});

// Load configuration
var dbOptions = new DbOptions();
builder.Configuration.GetSection(DbOptions.PATH).Bind(dbOptions);

var s3Options = new S3Options();
builder.Configuration.GetSection(S3Options.PATH).Bind(s3Options);

// Establish S3 session.
using var amazonS3 = new AmazonS3Uploader(s3Options.User, s3Options.Secret, s3Options.Endpoint);

// Create Postgre connection string
var connString = $"Host={dbOptions.Host};Username={dbOptions.User};Password={dbOptions.Password};Database={dbOptions.Database}";

Console.WriteLine(connString);

// Establish Postgres connection
await using var dataSource = new NpgsqlSlimDataSourceBuilder(connString).Build();

// Counter variable is used to increment image id
var counter = 0;

var app = builder.Build();

// Create Summary Prometheus metric to measure latency of the requests.
var summary = Metrics.CreateSummary("myapp_request_duration_seconds", "Duration of the request.", new SummaryConfiguration
{
    LabelNames = ["op"],
    Objectives = [new QuantileEpsilonPair(0.9, 0.01), new QuantileEpsilonPair(0.99, 0.001)]
});

// Enable the /metrics page to export Prometheus metrics.
app.MapMetrics();

// Create endpoint that returns the status of the application.
// Placeholder for the health check
app.MapGet("/healthz", () => Results.Ok("OK"));

// Create endpoint that returns a list of connected devices.
app.MapGet("/api/devices", () =>
{
    Device[] devices = [
        new("b0e42fe7-31a5-4894-a441-007e5256afea", "5F-33-CC-1F-43-82", "2.1.6"),
        new("0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", "EF-2B-C4-F5-D6-34", "2.1.5"),
        new("b16d0b53-14f1-4c11-8e29-b9fcef167c26", "62-46-13-B7-B3-A1", "3.0.0"),
        new("51bb1937-e005-4327-a3bd-9f32dcf00db8", "96-A8-DE-5B-77-14", "1.0.1"),
        new("e0a1d085-dce5-48db-a794-35640113fa67", "7E-3B-62-A6-09-12", "3.5.6")
    ];

    return Results.Ok(devices);
});

// Create endpoint that uoloades image to S3 and writes metadate to Postgres
app.MapGet("/api/images", async () =>
{
    // Generate a new image.
    var image = new Image($"cs-thumbnail-{counter}.png");

    // Get the current time to record the duration of the S3 request.
    var s3StartTime = Stopwatch.GetTimestamp();

    // Upload the image to S3.
    await amazonS3.Upload(s3Options.Bucket, image.ObjKey, s3Options.ImgPath);

    // Record the duration of the request to S3.
    summary.WithLabels(["s3"]).Observe(Stopwatch.GetElapsedTime(s3StartTime).TotalSeconds);

    // Get the current time to record the duration of the Database request.
    var dbStartTime = Stopwatch.GetTimestamp();

    // Prepare the database query to insert a record.
    const string sqlQuery = "INSERT INTO cs_image VALUES ($1, $2, $3)";

    // Execute the query to create a new image record.
    await using (var cmd = dataSource.CreateCommand(sqlQuery))
    {
        cmd.Parameters.AddWithValue(image.ImageUuid);
        cmd.Parameters.AddWithValue(image.ObjKey);
        cmd.Parameters.AddWithValue(image.CreatedAt);
        await cmd.ExecuteNonQueryAsync();
    }

    // Record the duration of the insert query.
    summary.WithLabels(["db"]).Observe(Stopwatch.GetElapsedTime(dbStartTime).TotalSeconds);

    // Increment the counter.
    counter++;

    return Results.Ok("Saved!");
});

app.Run();

[JsonSerializable(typeof(Device[]))]
internal partial class AppJsonSerializerContext : JsonSerializerContext;