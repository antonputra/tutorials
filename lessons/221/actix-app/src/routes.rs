use actix_web::{get, HttpRequest, HttpResponse};

use crate::device::Device;

// (Placeholder) Returns the status of the application.
#[get("/healthz")]
async fn health() -> HttpResponse {
    HttpResponse::Ok().body("OK")
}

/// Returns a list of connected devices.
#[get("/api/devices")]
async fn devices(request: HttpRequest) -> HttpResponse {
    let ip = request
        .headers()
        .get("X-Forwarded-For")
        .expect("X-Forwarded-For is missing");

    let device_ip = ip.to_str().unwrap();

    let device: Device = Device {
        id: 1,
        mac: String::from("EF-2B-C4-F5-D6-34"),
        firmware: String::from("2.1.5"),
        ip: String::from(device_ip),
    };

    HttpResponse::Ok().json(device)
}
