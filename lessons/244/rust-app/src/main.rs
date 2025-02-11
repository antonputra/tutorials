mod device;
mod routes;

use self::routes::{create_device, get_devices, health};

use axum::{routing::get, routing::post, Router};
use bb8::Pool;
use bb8_postgres::PostgresConnectionManager;
use std::env::var;
use tokio_postgres::NoTls;

#[tokio::main]
async fn main() {
    let host = var("POSTGRES_HOST").expect("The `POSTGRES_HOST` env variable is missing");
    let user = var("POSTGRES_USER").expect("The `POSTGRES_USER` env variable is missing");
    let pwd = var("POSTGRES_PWD").expect("The `POSTGRES_PWD` env variable is missing");
    let db = var("POSTGRES_DB").expect("The `POSTGRES_DB` env variable is missing");
    let size_s = var("POSTGRES_POOL").expect("The `POSTGRES_POOL` env variable is missing");
    let size = size_s.parse::<u32>().unwrap();

    let manager = PostgresConnectionManager::new_from_stringlike(
        format!("postgresql://{}:{}@{}:{}/{}", user, pwd, host, "5432", db,),
        NoTls,
    )
    .unwrap();

    let pool = Pool::builder().max_size(size).build(manager).await.unwrap();

    let app = Router::new()
        .route("/healthz", get(health))
        .route("/api/devices", get(get_devices))
        .route("/api/devices", post(create_device))
        .with_state(pool);

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
