mod models;
mod routes;

use ntex::http::KeepAlive;
use ntex::time::Seconds;
use ntex::web::{App, HttpServer, get};
use std::error::Error;

const PORT: u16 = 8080;
const THREADS: usize = 2;
const API_PATH: &'static str = "/api/v3/ticker/bookTicker";

#[ntex::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync>> {
    HttpServer::new(move || App::new().route(API_PATH, get().to(routes::get_tickers)))
        .bind(("0.0.0.0", PORT))?
        // Same 2 threads as other frameworks.
        .workers(THREADS)
        // Same 100 seconds KeepAlive as other frameworks.
        .keep_alive(KeepAlive::Timeout(Seconds::new(100)))
        .run()
        .await?;

    Ok(())
}
