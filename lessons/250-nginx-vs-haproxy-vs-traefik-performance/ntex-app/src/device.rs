use deadpool_postgres::Pool;
use ntex::http::{Response, StatusCode};
use ntex::web::error::InternalError;
use ntex::web::types::{Json, State};
use ntex::web::Responder;
use serde::{Deserialize, Serialize};
use std::error::Error;
use std::fmt::Debug;

#[derive(Debug, Serialize, Deserialize)]
pub struct Device {
    pub id: Option<i32>,
    pub mac: Box<str>,
    pub firmware: Box<str>,
}

pub async fn list_devices() -> impl Responder {
    let devices = [
        Device {
            id: Some(0),
            mac: Box::from("5F-33-CC-1F-43-82"),
            firmware: Box::from("2.1.6"),
        },
        Device {
            id: Some(1),
            mac: Box::from("44-39-34-5E-9C-F2"),
            firmware: Box::from("3.0.1"),
        },
        Device {
            id: Some(2),
            mac: Box::from("2B-6E-79-C7-22-1B"),
            firmware: Box::from("1.8.9"),
        },
        Device {
            id: Some(3),
            mac: Box::from("06-0A-79-47-18-E1"),
            firmware: Box::from("4.0.9"),
        },
        Device {
            id: Some(4),
            mac: Box::from("68-32-8F-00-B6-F4"),
            firmware: Box::from("5.0.0"),
        },
    ];

    Json(devices)
}

pub async fn create_device(
    pool: State<Pool>,
    Json(device): Json<Device>,
) -> Result<Response, InternalError<String>> {
    let conn = pool.get().await.map_err(map_error)?;

    let stmt = conn
        .prepare_cached("INSERT INTO rust_device (mac, firmware) VALUES ($1, $2) RETURNING id")
        .await
        .map_err(map_error)?;

    let row = conn
        .query_one(&stmt, &[&device.mac, &device.firmware])
        .await
        .map_err(map_error)?;

    let created = Device {
        id: row.try_get(0).map_err(map_error)?,
        mac: device.mac,
        firmware: device.firmware,
    };

    Ok(Response::Created().json(&created))
}

fn map_error<E: Error>(e: E) -> InternalError<String> {
    InternalError::new(e.to_string(), StatusCode::INTERNAL_SERVER_ERROR)
}
