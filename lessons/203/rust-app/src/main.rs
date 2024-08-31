use deadpool_postgres::Pool;

use actix_web::{get, App, HttpResponse, HttpServer};
use aws_sdk_s3::{primitives::ByteStream, Client};
use state::AppState;
use std::time::Instant;
use uuid::uuid;

use actix_web::middleware::Compress;
use actix_web::{web, Result};

use prometheus_client::encoding::text::encode;
pub mod config;
pub mod device;
pub mod image;
pub mod metrics;
pub mod state;

use device::Device;
use image::{generate_image, Image};
use metrics::Metrics;

use config::ConfigData;

// Returns Prometheus metrics.
#[get("/metrics")]
async fn get_metrics(state: web::Data<AppState>) -> Result<HttpResponse> {
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
            uuid: uuid!("b0e42fe7-31a5-4894-a441-007e5256afea"),
            mac: "5F-33-CC-1F-43-82".into(),
            firmware: "2.1.6".into(),
        },
        Device {
            uuid: uuid!("0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7"),
            mac: "EF-2B-C4-F5-D6-34".into(),
            firmware: "2.1.5".into(),
        },
        Device {
            uuid: uuid!("b16d0b53-14f1-4c11-8e29-b9fcef167c26"),
            mac: "62-46-13-B7-B3-A1".into(),
            firmware: "3.0.0".into(),
        },
        Device {
            uuid: uuid!("51bb1937-e005-4327-a3bd-9f32dcf00db8"),
            mac: "96-A8-DE-5B-77-14".into(),
            firmware: "1.0.1".into(),
        },
        Device {
            uuid: uuid!("e0a1d085-dce5-48db-a794-35640113fa67"),
            mac: "7E-3B-62-A6-09-12".into(),
            firmware: "3.5.6".into(),
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
async fn save_images(state: web::Data<AppState>) -> HttpResponse {
    // Generate a new image.
    let image = generate_image();

    // Upload the image to S3.
    if let Err(_) = upload(&state.config, &state.metrics, &state.s3_client, &image.key).await {
        return HttpResponse::BadRequest().body("Failed to upload to S3!");
    }

    // Save the image metadata to db.
    if let Err(_) = save(&state.metrics, &state.db_pool, &image).await {
        return HttpResponse::BadRequest().body("Failed to write to Database!");
    }

    HttpResponse::Ok().body("Saved!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the application state.
    let state = AppState::init().await;

    // Extract the port from the configuration.
    let port = state.config.config.port;

    HttpServer::new(move || {
        App::new()
            .wrap(Compress::default())
            .app_data(web::Data::new(state.clone()))
            .service(get_devices)
            .service(get_health)
            .service(save_images)
            .service(get_metrics)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}

// Uploads the image to S3.
async fn upload(
    config: &ConfigData,
    metrics: &Metrics,
    s3_client: &Client,
    obj_key: &String,
) -> Result<(), ResultError> {
    // Get the current time to record the duration of the request.
    let start = Instant::now();

    // Read the file from the local file system.
    let body = ByteStream::from_path(&config.s3.img_path).await.unwrap();

    // Upload the file to the S3 bucket (ignore the successful upload result).
    let _ = s3_client
        .put_object()
        .bucket(&config.s3.bucket)
        .key(obj_key)
        .body(body)
        .send()
        .await
        .map_err(|_| ResultError {})?;

    // Stop the timer to measure duration.
    let end = Instant::now();

    // Record the duration of the request to S3.
    let duration = end.duration_since(start).as_secs_f64();
    metrics.observe(String::from("s3"), duration);

    // Return the HTTP result.
    Ok(())
}

// Save inserts a newly generated image into the Postgres database.
async fn save(metrics: &Metrics, db_pool: &Pool, image: &Image) -> Result<(), ResultError> {
    // Get the current time to record the duration of the request.
    let start = Instant::now();

    // Create a client for the database.
    // The pool object is shared, and a client is obtained with each call.
    // Official ex. - https://github.com/actix/examples/blob/0523eea2f6a8a0fad66d0fbac2e067f7a0a137c6/databases/postgres/src/main.rs#L30
    let client = db_pool.get().await.map_err(|_| ResultError {})?;

    // Prepare the SQL query.
    let query = "INSERT INTO rust_image VALUES ($1, $2, $3)";
    let stmt = client.prepare(&query).await.map_err(|_| ResultError {})?;

    // Insert the record into the database (ignore the result of query execution).
    let _ = client
        .execute(&stmt, &[&image.uuid, &image.key, &image.created_at])
        .await
        .map_err(|_| ResultError {})?;

    // Stop the timer to measure duration.
    let end = Instant::now();

    // Record the duration of the request to Db.
    let duration = end.duration_since(start).as_secs_f64();
    metrics.observe(String::from("db"), duration);

    Ok(())
}

struct ResultError {}
