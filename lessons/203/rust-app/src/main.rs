use deadpool_postgres::tokio_postgres::NoTls;
use deadpool_postgres::Pool;
use deadpool_postgres::{Config, ManagerConfig, RecyclingMethod};

use std::sync::Mutex;

use actix_web::{get, App, HttpResponse, HttpServer};
use aws_config::BehaviorVersion;
use aws_sdk_s3::{config::Region, primitives::ByteStream, Client};
use std::path::Path;    

use actix_web::middleware::Compress;
use actix_web::{web, Result};
use std::time::SystemTime;

use prometheus_client::encoding::text::encode;
pub mod config;
pub mod device;
pub mod image;
pub mod metrics;

use device::Device;
use image::{generate_image, Image};
use metrics::{AppState, Metrics};

use config::{ConfigData, DbConfig, S3Config};

// Returns Prometheus metrics.
#[get("/metrics")]
async fn get_metrics(state: web::Data<Mutex<AppState>>) -> Result<HttpResponse> {
    let state = state.lock().unwrap();
    let mut body = String::new();

    encode(&mut body, &state.registry).unwrap();
    Ok(HttpResponse::Ok()
        .content_type("application/openmetrics-text; version=1.0.0; charset=utf-8")
        .body(body))
}

// Returns a list of connected devices.
#[get("/api/devices")]
async fn get_devices() -> HttpResponse {
    let devices = [
        Device {
            uuid: "b0e42fe7-31a5-4894-a441-007e5256afea",
            mac: "5F-33-CC-1F-43-82",
            firmware: "2.1.6",
        },
        Device {
            uuid: "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7",
            mac: "EF-2B-C4-F5-D6-34",
            firmware: "2.1.5",
        },
        Device {
            uuid: "b16d0b53-14f1-4c11-8e29-b9fcef167c26",
            mac: "62-46-13-B7-B3-A1",
            firmware: "3.0.0",
        },
        Device {
            uuid: "51bb1937-e005-4327-a3bd-9f32dcf00db8",
            mac: "96-A8-DE-5B-77-14",
            firmware: "1.0.1",
        },
        Device {
            uuid: "e0a1d085-dce5-48db-a794-35640113fa67",
            mac: "7E-3B-62-A6-09-12",
            firmware: "3.5.6",
        },
    ];

    HttpResponse::Ok().json(devices)
}

// (Placeholder) Returns the status of the application.
#[get("/healthz")]
async fn get_health() -> HttpResponse {
    HttpResponse::Ok().body("OK")
}

// Uploads an image to the S3 bucket and writes metadata to the database.
#[get("/api/images")]
async fn save_images(
    metrics: web::Data<Metrics>,
    config: web::Data<ConfigData>,
    s3_client: web::Data<Client>,
    db_pool: web::Data<Pool>,
) -> HttpResponse {
    // Generate a new image.
    let image = generate_image();

    // Upload the image to S3.
    if upload(config, metrics.clone(), s3_client, &image.key).await.is_err() {
        return HttpResponse::BadRequest().body("Failed to upload to S3!");
    }

    // Save the image metadata to db.
    if save(metrics.clone(), db_pool, image).await.is_err() {
        return HttpResponse::BadRequest().body("Failed to write to Database!");
    }

    HttpResponse::Ok().body("Saved!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Load the app configuration from a TOML file.
    let app_config = ConfigData::load("config.toml").unwrap();

    // Wrap the app configuration in the web::Data type.
    let app_config_data = web::Data::new(app_config.clone());

    // Create a connection pool for the PostgreSQL database.
    let db_pool = db_connect(app_config.db).await;
    let db_pool_data = web::Data::new(db_pool);

    // Create an S3 client.
    let s3_client = s3_connect(app_config.s3).await;
    let new_s3_client = web::Data::new(s3_client);

    // Create Prometheus metrics.
    let metrics = Metrics::new();
    let metrics_data = web::Data::new(metrics);

    // Create a new application state.
    let mut state = AppState::new();

    // Register a histogram to monitor the application.
    state.registry.register(
        "myapp_request_duration_seconds",
        "Duration of the request",
        metrics_data.request.clone(),
    );
    let state = web::Data::new(Mutex::new(state));

    HttpServer::new(move || {
        App::new()
            .wrap(Compress::default())
            .app_data(metrics_data.clone())
            .app_data(app_config_data.clone())
            .app_data(new_s3_client.clone())
            .app_data(db_pool_data.clone())
            .app_data(state.clone())
            .service(get_devices)
            .service(get_health)
            .service(save_images)
            .service(get_metrics)
    })
    .bind(("0.0.0.0", app_config.config.port))?
    .run()
    .await
}

// Initializes the S3 client.
async fn s3_connect(config: S3Config) -> Client {
    // Create region for the S3 bucket.
    let region = Region::new(config.region);
    // Create an AWS config with a custom endpoint to interact with MinIO.
    let cfg = aws_config::defaults(BehaviorVersion::latest()).endpoint_url(config.endpoint);

    // Establish a new session with the AWS S3 API.
    let cfg = cfg.region(region).load().await;

    // Return the S3 client.
    Client::new(&cfg)
}

// Create a connection pool to connect to PostgreSQL.
async fn db_connect(config: DbConfig) -> Pool {
    // Create a new connection pool config.
    let mut cfg = Config::new();

    // Provide settings to connect to the database.
    cfg.dbname = Some(config.database);
    cfg.user = Some(config.user);
    cfg.password = Some(config.password);
    cfg.host = Some(config.host);

    cfg.manager = Some(ManagerConfig {
        recycling_method: RecyclingMethod::Fast,
    });

    // Establish a connection with the database, or fail if unsuccessful.
    cfg.create_pool(None, NoTls).unwrap()
}

// Uploads the image to S3.
async fn upload(
    config: web::Data<ConfigData>,
    metrics: web::Data<Metrics>,
    s3_client: web::Data<Client>,
    obj_key: &str,
) -> Result<(), ResultError> {
    // Get the current time to record the duration of the request.
    let start = SystemTime::now();

    // Read the file from the local file system.
    let body = ByteStream::from_path(Path::new(&config.s3.img_path)).await;

    // Upload the file to the S3 bucket.
    s3_client
        .put_object()
        .bucket(&config.s3.bucket)
        .key(obj_key)
        .body(body.unwrap())
        .send()
        .await
        .map_err(|_| ResultError {})?;

    // Record the duration of the request to S3.
    let duration = start.elapsed().unwrap().as_secs_f64();
    metrics.observe("s3", duration);

    // Return the HTTP result.
    Ok(())
}

// Save inserts a newly generated image into the Postgres database.
async fn save(
    metrics: web::Data<Metrics>,
    db_pool: web::Data<Pool>,
    image: Image,
) -> Result<(), ResultError> {
    // Get the current time to record the duration of the request.
    let start = SystemTime::now();

    // Create a client for the database.
    // The pool object is shared, and a client is obtained with each call.
    // Official ex. - https://github.com/actix/examples/blob/0523eea2f6a8a0fad66d0fbac2e067f7a0a137c6/databases/postgres/src/main.rs#L30
    let client = db_pool.get().await.map_err(|_| ResultError {})?;

    // Get the object key from the image.
    let obj_key = image.key;

    // Prepare the SQL query.
    let query = "INSERT INTO rust_image VALUES ($1, $2, $3)";
    let stmt = client.prepare(&query).await.map_err(|_| ResultError {})?;

    // Insert the record into the database.
    client
        .query(&stmt, &[&image.uuid, &obj_key, &image.created_at])
        .await
        .map_err(|_| ResultError {})?;

    // Record the duration of the request to Db.
    let duration = start.elapsed().unwrap().as_secs_f64();
    metrics.observe("db", duration);

    Ok(())
}

struct ResultError {}
