use axum::{http::StatusCode, response::IntoResponse};

use crate::device::Device;

use axum::{extract::State, Json};
use bb8::Pool;
use bb8_postgres::PostgresConnectionManager;
use tokio_postgres::NoTls;

type ConnectionPool = Pool<PostgresConnectionManager<NoTls>>;

// (Placeholder) Returns the status of the application.
pub async fn health() -> impl IntoResponse {
    (StatusCode::OK, "OK")
}

/// Returns a list of connected devices.
pub async fn get_devices() -> impl IntoResponse {
    let devices = [
        Device {
            id: Some(0),
            mac: String::from("5F-33-CC-1F-43-82"),
            firmware: String::from("2.1.6"),
        },
        Device {
            id: Some(1),
            mac: String::from("44-39-34-5E-9C-F2"),
            firmware: String::from("3.0.1"),
        },
        Device {
            id: Some(2),
            mac: String::from("2B-6E-79-C7-22-1B"),
            firmware: String::from("1.8.9"),
        },
        Device {
            id: Some(3),
            mac: String::from("06-0A-79-47-18-E1"),
            firmware: String::from("4.0.9"),
        },
        Device {
            id: Some(4),
            mac: String::from("68-32-8F-00-B6-F4"),
            firmware: String::from("5.0.0"),
        },
    ];

    (StatusCode::OK, axum::Json(devices))
}

pub async fn create_device(
    State(pool): State<ConnectionPool>,
    Json(device): Json<Device>,
) -> Result<Json<Device>, (StatusCode, String)> {
    let conn = pool.get().await.map_err(internal_error)?;

    let row = conn
        .query_one(
            "INSERT INTO rust_device (mac, firmware) VALUES ($1, $2) RETURNING id",
            &[&device.mac, &device.firmware],
        )
        .await
        .map_err(internal_error)?;

    let res = Device {
        id: row.try_get(0).map_err(internal_error)?,
        mac: device.mac,
        firmware: device.firmware,
    };
    Ok(Json(res))
}

fn internal_error<E>(err: E) -> (StatusCode, String)
where
    E: std::error::Error,
{
    (StatusCode::INTERNAL_SERVER_ERROR, err.to_string())
}
