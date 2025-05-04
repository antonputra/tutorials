mod device;
mod health;

use crate::device::{create_device, list_devices};
use crate::health::health;
use deadpool_postgres::Runtime::Tokio1;
use deadpool_postgres::{ManagerConfig, Pool, SslMode};
use ntex::web::{get, post, App, HttpServer};
use std::env::var;
use std::error::Error;
use std::io::Write;
use tokio_postgres::NoTls;

const ENV_HTTP_PORT: &'static str = "HTTP_PORT";
const ENV_DB_CONNECTIONS: &'static str = "POSTGRES_POOL";
const ENV_DB_HOST: &'static str = "POSTGRES_HOST";
const ENV_DB_PORT: &'static str = "POSTGRES_PORT";
const ENV_DB_USER: &'static str = "POSTGRES_USER";
const ENV_DB_PASS: &'static str = "POSTGRES_PWD";
const ENV_DB_NAME: &'static str = "POSTGRES_DB";

const DEFAULT_HTTP_PORT: u16 = 8080;
const DEFAULT_DB_PORT: u16 = 5432;
const DEFAULT_DB_CONNECTIONS: usize = 16;
const DEFAULT_DB_HOST: &'static str = "127.0.0.1";
const DEFAULT_DB_USER: &'static str = "postgres";
const DEFAULT_DB_PASS: &'static str = "password";
const DEFAULT_DB_NAME: &'static str = "ntexdb";

#[ntex::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync>> {
    let http_port = var(ENV_HTTP_PORT).map_or(Ok(DEFAULT_HTTP_PORT), |val| val.parse())?;

    let pool = create_db_pool()?;

    writeln!(std::io::stdout(), "Starting server on port {}", http_port)?;
    HttpServer::new(move || {
        App::new()
            .state(pool.clone())
            .route("/healthz", get().to(health))
            .route("/api/devices", get().to(list_devices))
            .route("/api/devices", post().to(create_device))
    })
    .bind(("0.0.0.0", http_port))?
    .run()
    .await?;

    Ok(())
}

fn create_db_pool() -> Result<Pool, Box<dyn Error + Send + Sync>> {
    let db_port = var(ENV_DB_PORT).map_or(Ok(DEFAULT_DB_PORT), |val| val.parse())?;
    let db_host = var(ENV_DB_HOST).unwrap_or_else(|_| DEFAULT_DB_HOST.to_owned());
    let db_user = var(ENV_DB_USER).unwrap_or_else(|_| DEFAULT_DB_USER.to_owned());
    let db_pass = var(ENV_DB_PASS).unwrap_or_else(|_| DEFAULT_DB_PASS.to_owned());
    let db_name = var(ENV_DB_NAME).unwrap_or_else(|_| DEFAULT_DB_NAME.to_owned());
    let db_connections =
        var(ENV_DB_CONNECTIONS).map_or(Ok(DEFAULT_DB_CONNECTIONS), |val| val.parse())?;

    let pool_cfg = deadpool_postgres::PoolConfig::new(db_connections);
    let mut pg_cfg = deadpool_postgres::Config::new();
    pg_cfg.pool = Some(pool_cfg);
    pg_cfg.host = Some(db_host);
    pg_cfg.port = Some(db_port);
    pg_cfg.user = Some(db_user);
    pg_cfg.password = Some(db_pass);
    pg_cfg.dbname = Some(db_name);
    pg_cfg.manager = Some(ManagerConfig::default());
    pg_cfg.ssl_mode = Some(SslMode::Disable);

    Ok(pg_cfg.create_pool(Some(Tokio1), NoTls)?)
}
