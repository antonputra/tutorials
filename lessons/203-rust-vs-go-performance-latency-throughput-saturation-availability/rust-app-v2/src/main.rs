mod config;
mod device;
mod image;
mod metrics;
mod routes;
mod state;

use std::future::ready;

use axum::{http::StatusCode, routing::get, Router};
use metrics::setup_metrics_recorder;
use routes::save_images;

use self::{config::Config, routes::devices, state::AppState};

#[tokio::main]
async fn main() {
    // Load the app configuration from a TOML file.
    let config = match Config::load("config.toml").await {
        Ok(config) => config,
        Err(err) => {
            eprintln!("Failed to load config: {:?}", err);
            return;
        }
    };

    // Extract the port from the configuration.
    let port = config.app.port;

    // Set up the metrics recorder.
    let metrics_recorder = match setup_metrics_recorder() {
        Ok(recorder) => recorder,
        Err(err) => {
            eprintln!("Failed to set up metrics recorder: {:?}", err);
            return;
        }
    };

    // Create the application state from the configuration.
    let state = match AppState::from_config(config).await {
        Ok(state) => state,
        Err(err) => {
            eprintln!("Failed to create application state state: {:?}", err);
            return;
        }
    };

    // Create the application router.
    let app = Router::new()
        .route("/healthz", get(|| async { (StatusCode::OK, "OK") }))
        .route("/api/devices", get(devices))
        .route("/api/images", get(save_images))
        .route("/metrics", get(move || ready(metrics_recorder.render())))
        .with_state(state);

    // Bind the server to the configured port.
    let listener = match tokio::net::TcpListener::bind(format!("0.0.0.0:{}", port)).await {
        Ok(listener) => listener,
        Err(err) => {
            eprintln!("Failed to bind to port {}: {:?}", port, err);
            return;
        }
    };

    // Start the server.
    if let Err(err) = axum::serve(listener, app).await {
        eprintln!("Failed to start server: {:?}", err);
    }
}
