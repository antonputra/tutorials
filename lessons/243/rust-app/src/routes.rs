use bytes::Bytes;
use http_body_util::{combinators::BoxBody, BodyExt, Empty, Full};
use hyper::{Method, Request, Response, StatusCode};

use crate::device::Device;

fn devices() -> Result<Response<BoxBody<bytes::Bytes, hyper::Error>>, hyper::Error> {
    let devices = [
        Device {
            id: 1,
            uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
            mac: "EF-2B-C4-F5-D6-34",
            firmware: "2.1.5",
            created_at: "2024-05-28T15:21:51.137Z",
            updated_at: "2024-05-28T15:21:51.137Z",
        },
        Device {
            id: 2,
            uuid: "d2293412-36eb-46e7-9231-af7e9249fffe",
            mac: "E7-34-96-33-0C-4C",
            firmware: "1.0.3",
            created_at: "2024-01-28T15:20:51.137Z",
            updated_at: "2024-01-28T15:20:51.137Z",
        },
        Device {
            id: 3,
            uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
            mac: "68-93-9B-B5-33-B9",
            firmware: "4.3.1",
            created_at: "2024-08-28T15:18:21.137Z",
            updated_at: "2024-08-28T15:18:21.137Z",
        },
        Device {
            id: 4,
            uuid: "ab4efcd0-f542-4944-9dd9-0ad844dfcbd3",
            mac: "E7-6F-69-99-F1-ED",
            firmware: "6.2.0",
            created_at: "2024-08-29T15:18:21.137Z",
            updated_at: "2024-08-29T15:18:21.137Z",
        },
        Device {
            id: 5,
            uuid: "9e725cbc-2c4e-446c-a274-962531f90927",
            mac: "9F-57-E5-1F-F5-6B",
            firmware: "0.6.4",
            created_at: "2024-18-28T15:18:21.137Z",
            updated_at: "2024-18-28T15:18:21.137Z",
        },
    ];

    let body = serde_json::to_string(&devices).unwrap();

    Ok(Response::new(full(Bytes::from(body))))
}

pub async fn routes(
    req: Request<hyper::body::Incoming>,
) -> Result<Response<BoxBody<Bytes, hyper::Error>>, hyper::Error> {
    match (req.method(), req.uri().path()) {
        (&Method::GET, "/api/devices") => devices(),

        _ => {
            let mut not_found = Response::new(empty());
            *not_found.status_mut() = StatusCode::NOT_FOUND;
            Ok(not_found)
        }
    }
}

fn empty() -> BoxBody<Bytes, hyper::Error> {
    Empty::<Bytes>::new()
        .map_err(|never| match never {})
        .boxed()
}
fn full<T: Into<Bytes>>(chunk: T) -> BoxBody<Bytes, hyper::Error> {
    Full::new(chunk.into())
        .map_err(|never| match never {})
        .boxed()
}
