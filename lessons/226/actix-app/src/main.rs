mod device;
mod routes;

use actix_web::{App, HttpServer};
use std::env;

use self::routes::devices;
use self::routes::health;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let port: u16 = env::var("RUST_PORT")
        .expect("RUST_PORT env MUST be set!")
        .parse()
        .unwrap();

    HttpServer::new(|| App::new().service(devices).service(health))
        .workers(1)
        .bind(("0.0.0.0", port))?
        .run()
        .await
}
