use anyhow::{Context, Error};
use serde::Deserialize;
use tokio::fs;
use toml;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub app: AppConfig,
    pub db: DbConfig,
    pub s3: S3Config,
}

#[derive(Debug, Clone, Deserialize)]
pub struct AppConfig {
    pub port: u16,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DbConfig {
    pub user: String,
    pub password: String,
    pub host: String,
    pub database: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct S3Config {
    pub region: String,
    pub bucket: String,
    pub endpoint: String,
    #[allow(dead_code)] // This field is not used in the example.
    pub path_style: bool,
    pub img_path: String,
}

impl Config {
    pub async fn load(filename: &str) -> Result<Self, Error> {
        let contents = fs::read_to_string(filename)
            .await
            .with_context(|| format!("Failed to read config file: {}", filename))?;

        toml::from_str(&contents).with_context(|| format!("Failed to parse config file: {}", filename))
    }
}
