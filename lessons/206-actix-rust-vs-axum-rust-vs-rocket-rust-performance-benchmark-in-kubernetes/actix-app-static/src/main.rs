mod routes;

use actix_web::{App, HttpServer};

use self::routes::devices;
use self::routes::health;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().service(devices).service(health))
        .bind(("0.0.0.0", 8080))?
        .run()
        .await
}
