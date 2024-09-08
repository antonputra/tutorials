use axum::{extract::State, http::StatusCode, response::IntoResponse};

use crate::{device::Device, image::Image, state::AppState};

/// Returns a list of connected devices.
pub async fn devices() -> impl IntoResponse {
    let devices = [
        Device {
            uuid: "b0e42fe7-31a5-4894-a441-007e5256afea",
            mac: "5F-33-CC-1F-43-82",
            firmware: "2.1.6",
        },
        Device {
            uuid: "0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7",
            mac: "EF-2B-C4-F5-D6-34",
            firmware: "2.1.5",
        },
        Device {
            uuid: "b16d0b53-14f1-4c11-8e29-b9fcef167c26",
            mac: "62-46-13-B7-B3-A1",
            firmware: "3.0.0",
        },
        Device {
            uuid: "51bb1937-e005-4327-a3bd-9f32dcf00db8",
            mac: "96-A8-DE-5B-77-14",
            firmware: "1.0.1",
        },
        Device {
            uuid: "e0a1d085-dce5-48db-a794-35640113fa67",
            mac: "7E-3B-62-A6-09-12",
            firmware: "3.5.6",
        },
    ];

    (StatusCode::OK, axum::Json(devices))
}

/// Uploads an image to the S3 bucket and writes metadata to the database.
pub async fn save_images(State(state): State<AppState>) -> impl IntoResponse {
    // Generate a new image.
    let image = Image::generate();

    // Start both the S3 upload and DB save concurrently.
    let (upload_result, save_result) = tokio::join!(image.upload(&state), image.save(&state));

    // Check results and return appropriate response.
    if let Err(err) = upload_result {
        return (StatusCode::INTERNAL_SERVER_ERROR, err.to_string());
    }

    if let Err(err) = save_result {
        return (StatusCode::INTERNAL_SERVER_ERROR, err.to_string());
    }

    (StatusCode::OK, "Saved!".to_owned())
}
