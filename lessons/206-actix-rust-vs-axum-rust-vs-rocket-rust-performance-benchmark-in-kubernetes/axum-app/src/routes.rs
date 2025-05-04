use axum::{http::StatusCode, response::IntoResponse};

use crate::device::Device;

// (Placeholder) Returns the status of the application.
pub async fn health() -> impl IntoResponse {
    (StatusCode::OK, "OK")
}

/// Returns a list of connected devices.
pub async fn devices() -> impl IntoResponse {
    let devices = [
        Device {
            id: 1,
            mac: String::from("5F-33-CC-1F-43-82"),
            firmware: String::from("2.1.6"),
        },
        Device {
            id: 2,
            mac: String::from("EF-2B-C4-F5-D6-34"),
            firmware: String::from("2.1.5"),
        },
        Device {
            id: 3,
            mac: String::from("62-46-13-B7-B3-A1"),
            firmware: String::from("3.0.0"),
        },
        Device {
            id: 4,
            mac: String::from("96-A8-DE-5B-77-14"),
            firmware: String::from("1.0.1"),
        },
        Device {
            id: 5,
            mac: String::from("7E-3B-62-A6-09-12"),
            firmware: String::from("3.5.6"),
        },
    ];

    (StatusCode::OK, axum::Json(devices))
}
