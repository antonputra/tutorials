use axum::{
    body::Bytes,
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};

use crate::device::{Device, DeviceData};

use axum::extract::State;
use deadpool_postgres::Pool;

// (Placeholder) Returns the status of the application.
pub async fn health() -> impl IntoResponse {
    (StatusCode::OK, "OK")
}

/// Returns a list of connected devices.
pub async fn get_devices() -> impl IntoResponse {
    let devices = [
        Device {
            id: 0,
            data: DeviceData {
                mac: "5F-33-CC-1F-43-82",
                firmware: "2.1.6",
            },
        },
        Device {
            id: 1,
            data: DeviceData {
                mac: "44-39-34-5E-9C-F2",
                firmware: "3.0.1",
            },
        },
        Device {
            id: 2,
            data: DeviceData {
                mac: "2B-6E-79-C7-22-1B",
                firmware: "1.8.9",
            },
        },
        Device {
            id: 3,
            data: DeviceData {
                mac: "06-0A-79-47-18-E1",
                firmware: "4.0.9",
            },
        },
        Device {
            id: 4,
            data: DeviceData {
                mac: "68-32-8F-00-B6-F4",
                firmware: "5.0.0",
            },
        },
    ];

    (StatusCode::OK, Json(devices))
}

pub async fn create_device(
    State(pool): State<Pool>,
    bytes: Bytes,
) -> Result<Response, (StatusCode, String)> {
    let conn = pool.get().await.map_err(internal_error)?;

    let device: DeviceData = serde_json::from_slice(&bytes).map_err(|err| {
        (
            StatusCode::BAD_REQUEST,
            format!("Failed to parse request body: {}", err),
        )
    })?;

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
        data: device,
    };

    Ok(Json(res).into_response())
}

fn internal_error<E>(err: E) -> (StatusCode, String)
where
    E: std::error::Error,
{
    (StatusCode::INTERNAL_SERVER_ERROR, err.to_string())
}
