use actix_web::{get, HttpResponse};

use crate::device::Device;

// (Placeholder) Returns the status of the application.
#[get("/healthz")]
async fn health() -> HttpResponse {
    HttpResponse::Ok().body("OK")
}

/// Returns a list of connected devices.
#[get("/api/devices")]
async fn devices() -> HttpResponse {
    let devices = [Device {
        id: 1,
        mac: "EF-2B-C4-F5-D6-34",
        firmware: "2.1.5",
    }];

    HttpResponse::Ok().json(devices)
}
