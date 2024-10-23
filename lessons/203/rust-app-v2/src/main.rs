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

use anyhow::Context;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Load the app configuration from a TOML file.
    let config = Config::load("config.toml").await.context("Failed to load config")?;

    // Extract the port from the configuration.
    let port = config.app.port;

    // Set up the metrics recorder.
    let metrics_recorder = setup_metrics_recorder().context("Failed to set up metrics recorder")?;

    // Create the application state from the configuration.
    let state = AppState::from_config(config).await.context("Failed to create application state state")?;

    // Create the application router.
    let app = Router::new()
        .route("/healthz", get(|| async { (StatusCode::OK, "OK") }))
        .route("/api/devices", get(devices))
        .route("/api/images", get(save_images))
        .route("/metrics", get(move || ready(metrics_recorder.render())))
        .with_state(state);

    // Bind the server to the configured port.
    let listener = tokio::net::TcpListener::bind(("0.0.0.0", port)).await.with_context(|| format!("Failed to bind to port {}", port))?;

    // Start the server.
    axum::serve(listener, app).await.context("Failed to start server")?;

    Ok(())
}
