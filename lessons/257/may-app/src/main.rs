mod models;
mod routes;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

use crate::routes::{Bench, HttpServer};
use may_minihttp::{HttpService, HttpServiceFactory, Request, Response};
use std::io;

const PORT: u16 = 8080;
const THREADS: usize = 2;
const API_PATH: &str = "/api/v3/ticker/bookTicker";

impl HttpService for Bench {
    fn call(&mut self, req: Request, rsp: &mut Response) -> io::Result<()> {
        match req.path() {
            API_PATH => {
                rsp.header("Content-Type: application/json");
                let tickers = routes::get_tickers();

                let json_bytes = serde_json::to_vec(&tickers).map_err(io::Error::other)?;
                rsp.body_mut().extend_from_slice(&json_bytes);
            }
            _ => {
                rsp.status_code(404, "Not Found");
            }
        }
        Ok(())
    }
}

impl HttpServiceFactory for HttpServer {
    type Service = Bench;

    fn new_service(&self, _id: usize) -> Self::Service {
        Bench {}
    }
}

fn main() {
    may::config().set_workers(THREADS);
    let server = HttpServer {};
    let address = format!("0.0.0.0:{}", PORT);

    println!("Starting http server: {}", address);
    server.start(address).unwrap().join().unwrap();
}
