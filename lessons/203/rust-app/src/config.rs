use serde_derive::Deserialize;
use std::fmt;
use std::fs;
use toml;

#[derive(Clone, Deserialize)]
pub struct ConfigData {
    pub config: AppConfig,
    pub db: DbConfig,
    pub s3: S3Config,
}

#[derive(Clone, Deserialize)]
pub struct AppConfig {
    pub port: u16,
}

#[derive(Clone, Deserialize)]
pub struct DbConfig {
    pub user: String,
    pub password: String,
    pub host: String,
    pub database: String,
}

#[derive(Clone, Deserialize)]
pub struct S3Config {
    pub region: String,
    pub bucket: String,
    pub endpoint: String,
    pub path_style: bool,
    pub img_path: String,
}

#[derive(Debug, Clone)]
pub struct ConfigError {
    filename: String,
    message: String,
    error: String,
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Error: {}, file: {}, reason: {}",
            self.message, self.filename, self.error
        )
    }
}

impl ConfigData {
    pub fn load(filename: &str) -> Result<Self, ConfigError> {
        let contents = match fs::read_to_string(filename) {
            Ok(c) => c,
            Err(e) => {
                return Err(ConfigError {
                    filename: filename.to_string(),
                    message: String::from("Failed to read config"),
                    error: e.to_string(),
                })
            }
        };

        let data: ConfigData = match toml::from_str(&contents) {
            Ok(c) => c,
            Err(e) => {
                return Err(ConfigError {
                    filename: filename.to_string(),
                    message: String::from("Failed to parse config"),
                    error: e.to_string(),
                })
            }
        };

        Ok(data)
    }
}
