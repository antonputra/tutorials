using Prometheus;
using System.Diagnostics;
using Npgsql;

// Initialize the Web App
var builder = WebApplication.CreateBuilder(args);

// Load app config from file.
var config = new ConfigurationBuilder().AddJsonFile("appsettings.json").Build();
var appConfig = new Config(config);

// Establish S3 session.
var amazonS3 = new AmazonS3Uploader(appConfig.User, appConfig.Secret, appConfig.S3Endpoint);

// Create Postgre connection string
var connString = string.Format("Host={0};Username={1};Password={2};Database={3}", appConfig.DbHost, appConfig.DbUser, appConfig.DbPassword, appConfig.DbDatabase);

Console.WriteLine(connString);

// Establish Postgres connection
await using var dataSource = NpgsqlDataSource.Create(connString);

// Conuter variable is used to increment image id
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
app.MapGet("/healthz", () => "OK");

// Create endpoint that returns a list of connected devices.
app.MapGet("/api/devices", () =>
{
    Device[] devices = [
        new() { Uuid = "b0e42fe7-31a5-4894-a441-007e5256afea", Mac = "5F-33-CC-1F-43-82", Firmware = "2.1.6" },
        new() { Uuid = "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", Mac = "EF-2B-C4-F5-D6-34", Firmware = "2.1.5" },
        new() { Uuid = "b16d0b53-14f1-4c11-8e29-b9fcef167c26", Mac = "62-46-13-B7-B3-A1", Firmware = "3.0.0" },
        new() { Uuid = "51bb1937-e005-4327-a3bd-9f32dcf00db8", Mac = "96-A8-DE-5B-77-14", Firmware = "1.0.1" },
        new() { Uuid = "e0a1d085-dce5-48db-a794-35640113fa67", Mac = "7E-3B-62-A6-09-12", Firmware = "3.5.6" }
    ];

    return devices;
});

// Create endpoint that uoloades image to S3 and writes metadate to Postgres
app.MapGet("/api/images", async () =>
{
    // Generate a new image.
    var image = new Image(string.Format("cs-thumbnail-{0}.png", counter));

    // Get the current time to record the duration of the S3 request.
    var s3Stopwatch = Stopwatch.StartNew();

    // Upload the image to S3.
    await amazonS3.Upload(appConfig.S3Bucket, image.ObjKey, appConfig.S3ImgPath);

    // Record the duration of the request to S3.
    s3Stopwatch.Stop();
    summary.WithLabels(["s3"]).Observe(s3Stopwatch.Elapsed.TotalSeconds);

    // Get the current time to record the duration of the Database request.
    var dBStopwatch = Stopwatch.StartNew();

    // Prepare the database query to insert a record.
    var sqlQuery = string.Format("INSERT INTO {0} VALUES ($1, $2, $3)", "cs_image");

    // Execute the query to create a new image record.
    await using (var cmd = dataSource.CreateCommand(sqlQuery))
    {
        cmd.Parameters.AddWithValue(image.ImageUuid);
        cmd.Parameters.AddWithValue(image.ObjKey);
        cmd.Parameters.AddWithValue(image.CreatedAt);
        await cmd.ExecuteNonQueryAsync();
    }

    // Record the duration of the insert query.
    dBStopwatch.Stop();
    summary.WithLabels(["db"]).Observe(dBStopwatch.Elapsed.TotalSeconds);

    // Icrement counter.
    counter++;

    return "Saved!";
});

app.Run();
