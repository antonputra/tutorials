mod config;
mod device;
mod image;
mod metrics;
mod routes;
mod state;

use std::{
    future::ready,
    io,
    net::{SocketAddr, ToSocketAddrs},
    time::Duration,
};

use axum::{http::StatusCode, routing::get, Router};
use metrics::setup_metrics_recorder;
use routes::save_images;
use socket2::{Domain, Socket, Type};

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
    let listener = match create_listener(format!("0.0.0.0:{}", port)) {
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

fn create_listener<A: ToSocketAddrs>(addr: A) -> io::Result<tokio::net::TcpListener> {
    let mut addrs = addr.to_socket_addrs()?;
    let addr = addrs.next().unwrap();
    let listener = match &addr {
        SocketAddr::V4(_) => Socket::new(Domain::IPV4, Type::STREAM, None)?,
        SocketAddr::V6(_) => Socket::new(Domain::IPV6, Type::STREAM, None)?,
    };

    listener.set_nonblocking(true)?;
    listener.set_nodelay(true)?;
    listener.set_reuse_address(true)?;
    listener.set_linger(Some(Duration::from_secs(0)))?;
    listener.bind(&addr.into())?;
    listener.listen(i32::MAX)?;

    let listener = std::net::TcpListener::from(listener);
    let listener = tokio::net::TcpListener::from_std(listener)?;
    Ok(listener)
}
