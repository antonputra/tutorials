mod device;
mod routes;

use self::routes::{create_device, get_devices, health};

use axum::{routing::get, routing::post, Router};
use deadpool_postgres::Runtime::Tokio1;
use deadpool_postgres::{ManagerConfig, SslMode};
use std::env::var;
use tokio_postgres::NoTls;

#[tokio::main]
async fn main() {
    let host = var("POSTGRES_HOST").expect("The `POSTGRES_HOST` env variable is missing");
    let user = var("POSTGRES_USER").expect("The `POSTGRES_USER` env variable is missing");
    let pwd = var("POSTGRES_PWD").expect("The `POSTGRES_PWD` env variable is missing");
    let db = var("POSTGRES_DB").expect("The `POSTGRES_DB` env variable is missing");
    let size_s = var("POSTGRES_POOL").expect("The `POSTGRES_POOL` env variable is missing");
    let size = size_s.parse::<usize>().unwrap();

    let pool_cfg = deadpool_postgres::PoolConfig::new(size);
    let mut config = deadpool_postgres::Config::new();
    config.pool = Some(pool_cfg);
    config.port = Some(5432);
    config.host = Some(host);
    config.user = Some(user);
    config.password = Some(pwd);
    config.dbname = Some(db);
    config.manager = Some(ManagerConfig::default());
    config.ssl_mode = Some(SslMode::Disable);

    let pool = config.create_pool(Some(Tokio1), NoTls).unwrap();

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
