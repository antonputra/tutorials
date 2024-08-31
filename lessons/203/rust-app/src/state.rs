use std::sync::Arc;

use aws_config::{BehaviorVersion, Region};
use aws_sdk_s3::Client;
use deadpool_postgres::{Config, ManagerConfig, Pool, RecyclingMethod};
use prometheus_client::registry::Registry;
use tokio_postgres::NoTls;

use crate::{
    config::{ConfigData, DbConfig, S3Config},
    metrics::Metrics,
};

#[derive(Clone)]
pub struct AppState {
    pub config: Arc<ConfigData>,
    pub db_pool: Pool,
    pub s3_client: Client,
    pub metrics: Arc<Metrics>,
    pub registry: Arc<Registry>,
}

impl AppState {
    pub async fn init() -> Self {
        // Load the app configuration from a TOML file.
        let config_file = "config.toml";
        let config = ConfigData::load(config_file).await.unwrap();

        // Create a connection pool for the PostgreSQL database.
        let db_pool = db_connect(&config.db).await;

        // Create an S3 client.
        let s3_client = s3_connect(&config.s3).await;

        // Create Prometheus metrics.
        let metrics = Metrics::new();

        // Register a histogram to monitor the application.
        let mut registry = Registry::default();
        registry.register(
            "myapp_request_duration_seconds",
            "Duration of the request",
            metrics.request.clone(),
        );

        AppState {
            config: Arc::new(config),
            db_pool,
            s3_client,
            metrics: Arc::new(metrics),
            registry: Arc::new(registry),
        }
    }
}

// Create a connection pool to connect to PostgreSQL.
async fn db_connect(config: &DbConfig) -> Pool {
    // Create a new connection pool config.
    let mut cfg = Config::new();

    // Provide settings to connect to the database.
    cfg.dbname = Some(config.database.clone());
    cfg.user = Some(config.user.clone());
    cfg.password = Some(config.password.clone());
    cfg.host = Some(config.host.clone());

    cfg.manager = Some(ManagerConfig {
        recycling_method: RecyclingMethod::Fast,
    });

    // Establish a connection with the database, or fail if unsuccessful.
    cfg.create_pool(None, NoTls).unwrap()
}

// Initializes the S3 client.
async fn s3_connect(config: &S3Config) -> Client {
    // Create region for the S3 bucket.
    let region = Region::new(config.region.clone());
    // Create an AWS config with a custom endpoint to interact with MinIO.
    let cfg = aws_config::defaults(BehaviorVersion::latest()).endpoint_url(&config.endpoint);

    // Establish a new session with the AWS S3 API.
    let cfg = cfg.region(region).load().await;

    // Return the S3 client.
    Client::new(&cfg)
}
