use std::sync::Arc;

use anyhow::{Context, Error};
use aws_config::BehaviorVersion;
use aws_sdk_s3::{config::Region, Client};
use deadpool_postgres::{tokio_postgres::NoTls, ManagerConfig, Pool, RecyclingMethod, Runtime};

use crate::config::{Config, DbConfig, S3Config};

#[derive(Clone)]
pub struct AppState {
    pub config: Arc<Config>,
    pub db_pool: Pool,
    pub s3_client: Client,
}

impl AppState {
    pub async fn from_config(config: Config) -> Result<Self, Error> {
        let db_pool = Self::db_connect(&config.db).context("Failed to connect to database")?;
        let s3_client = Self::s3_connect(&config.s3).await;

        Ok(Self {
            config: Arc::new(config),
            db_pool,
            s3_client,
        })
    }

    // Create a connection pool to connect to PostgreSQL.
    fn db_connect(config: &DbConfig) -> Result<Pool, Error> {
        // Create a new connection pool config.
        let mut cfg = deadpool_postgres::Config::new();

        // Provide settings to connect to the database.
        cfg.dbname = Some(config.database.to_owned());
        cfg.user = Some(config.user.to_owned());
        cfg.password = Some(config.password.to_owned());
        cfg.host = Some(config.host.to_owned());

        cfg.manager = Some(ManagerConfig {
            recycling_method: RecyclingMethod::Fast,
        });

        // Establish a connection with the database, or fail if unsuccessful.
        cfg.create_pool(Some(Runtime::Tokio1), NoTls)
            .context("Failed to create database pool")
    }

    // Initializes the S3 client.
    async fn s3_connect(config: &S3Config) -> Client {
        // Create region for the S3 bucket.
        let region = Region::new(config.region.to_owned());

        // Create an AWS config with a custom endpoint to interact with MinIO.
        let cfg = aws_config::defaults(BehaviorVersion::latest()).endpoint_url(&config.endpoint);

        // Establish a new session with the AWS S3 API.
        let cfg = cfg.region(region).load().await;

        // Return the S3 client.
        Client::new(&cfg)
    }
}
