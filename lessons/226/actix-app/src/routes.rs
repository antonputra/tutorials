use actix_web::{get, HttpRequest, HttpResponse};
use log::debug;

use crate::device::Device;

#[get("/healthz")]
async fn health() -> HttpResponse {
    HttpResponse::Ok().body("OK")
}

#[get("/api/devices")]
async fn devices(req: HttpRequest) -> HttpResponse {
    let mut headers = Vec::new();
    for val in req.headers().iter() {
        headers.push(val);
    }

    debug!(
        "{} {} {:?} Headers: {:?}",
        req.method(),
        req.path(),
        req.version(),
        headers
    );

    let device: Device = Device {
        uuid: String::from("ca2d109e-8486-4516-83c8-f6373afe4763"),
        mac: String::from("EF-2B-C4-F5-D6-34"),
        firmware: String::from("2.1.5"),
    };

    HttpResponse::Ok().json(device)
}
