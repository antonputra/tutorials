use axum::{routing::get, Json, Router};
use axum_prometheus::PrometheusMetricLayer;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct Device {
    uuid: String,
    mac: String,
    firmware: String,
}

#[tokio::main]
async fn main() {
    let (prometheus_layer, metric_handle) = PrometheusMetricLayer::pair();
    let app = Router::new()
        .route("/api-nginx/devices", get(get_devices))
        .route("/api-apache/devices", get(get_devices))
        .route("/metrics", get(|| async move { metric_handle.render() }))
        .layer(prometheus_layer);

    axum::Server::bind(&"0.0.0.0:8080".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn get_devices() -> Json<Vec<Device>> {
    let mut devices = Vec::new();
    devices.push(Device {
        uuid: String::from("asd"),
        mac: String::from("5F-33-CC-1F-43-82"),
        firmware: String::from("2.1.6"),
    });
    devices.push(Device {
        uuid: String::from("asd"),
        mac: String::from("EF-2B-C4-F5-D6-34"),
        firmware: String::from("2.1.6"),
    });

    Json(devices)
}
