mod models;
mod routes;

use self::routes::get_tickers;

use axum::{Router, routing::get};

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

const PORT: u16 = 8080;
const API_PATH: &str = "/api/v3/ticker/bookTicker";

#[tokio::main]
async fn main() {
    // Keep alive enabled by default.
    let app = Router::new().route(API_PATH, get(get_tickers));

    // Bind the server to the configured port.
    let listener = match tokio::net::TcpListener::bind(format!("0.0.0.0:{}", PORT)).await {
        Ok(listener) => listener,
        Err(err) => {
            eprintln!("Failed to bind to port {}: {:?}", PORT, err);
            return;
        }
    };

    // Start the server.
    if let Err(err) = axum::serve(listener, app).await {
        eprintln!("Failed to start server: {:?}", err);
    }
}
