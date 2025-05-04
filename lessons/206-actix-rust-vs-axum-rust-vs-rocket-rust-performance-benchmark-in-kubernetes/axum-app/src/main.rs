mod device;
mod routes;

use axum::{routing::get, Router};

use self::routes::devices;
use self::routes::health;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[tokio::main]
async fn main() {
    // Create the application router.
    let app = Router::new()
        .route("/healthz", get(health))
        .route("/api/devices", get(devices));

    // Bind the server to the configured port.
    let listener = match tokio::net::TcpListener::bind(format!("0.0.0.0:{}", 8080)).await {
        Ok(listener) => listener,
        Err(err) => {
            eprintln!("Failed to bind to port {}: {:?}", 8080, err);
            return;
        }
    };

    // Start the server.
    if let Err(err) = axum::serve(listener, app).await {
        eprintln!("Failed to start server: {:?}", err);
    }
}
