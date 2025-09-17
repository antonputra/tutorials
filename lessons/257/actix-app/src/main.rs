mod models;
mod routes;

use actix_web::{App, HttpServer, web};

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

const PORT: u16 = 8080;
const THREADS: usize = 2;
const API_PATH: &'static str = "/api/v3/ticker/bookTicker";

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Simulate Binance API
    HttpServer::new(|| App::new().route(API_PATH, web::get().to(routes::get_tickers)))
        // Same 2 threads as other frameworks.
        .workers(THREADS)
        // Same 100 seconds KeepAlive as other frameworks.
        .keep_alive(std::time::Duration::from_secs(100))
        .bind(("0.0.0.0", PORT))?
        .run()
        .await
}
