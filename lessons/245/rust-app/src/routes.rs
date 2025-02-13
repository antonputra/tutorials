use axum::{http::StatusCode, response::IntoResponse};

use crate::device::Device;

use axum::{extract::State, Json};
use deadpool_postgres::Pool;

// (Placeholder) Returns the status of the application.
pub async fn health() -> impl IntoResponse {
    (StatusCode::OK, "OK")
}

/// Returns a list of connected devices.
pub async fn get_devices() -> impl IntoResponse {
    // Match C++ implementation
    let device = Device {
        id: Some(0),
        mac: Box::from("5F-33-CC-1F-43-82"),
        firmware: Box::from("2.1.6"),
    };

    // TODO: keep for the round 2
    // let devices = [
    //     Device {
    //         id: Some(0),
    //         mac: Box::from("5F-33-CC-1F-43-82"),
    //         firmware: Box::from("2.1.6"),
    //     },
    //     Device {
    //         id: Some(1),
    //         mac: Box::from("44-39-34-5E-9C-F2"),
    //         firmware: Box::from("3.0.1"),
    //     },
    //     Device {
    //         id: Some(2),
    //         mac: Box::from("2B-6E-79-C7-22-1B"),
    //         firmware: Box::from("1.8.9"),
    //     },
    //     Device {
    //         id: Some(3),
    //         mac: Box::from("06-0A-79-47-18-E1"),
    //         firmware: Box::from("4.0.9"),
    //     },
    //     Device {
    //         id: Some(4),
    //         mac: Box::from("68-32-8F-00-B6-F4"),
    //         firmware: Box::from("5.0.0"),
    //     },
    // ];

    (StatusCode::OK, Json(device))
}

pub async fn create_device(
    State(pool): State<Pool>,
    Json(device): Json<Device>,
) -> Result<Json<Device>, (StatusCode, String)> {
    let conn = pool.get().await.map_err(internal_error)?;

    let stmt = conn
        .prepare_cached("INSERT INTO rust_device (mac, firmware) VALUES ($1, $2) RETURNING id")
        .await
        .map_err(internal_error)?;

    let row = conn
        .query_one(&stmt, &[&device.mac, &device.firmware])
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
