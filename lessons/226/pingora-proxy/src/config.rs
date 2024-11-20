use serde::Deserialize;
use std::fs;
use toml;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub proxy: ProxyConfig,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ProxyConfig {
    pub upstreams: Vec<String>,
    pub port: usize,
    pub tls_cert: String,
    pub tls_key: String,
}

impl Config {
    pub fn load(filename: &str) -> Self {
        let contents =
            fs::read_to_string(filename).expect(format!("failed to read {}", filename).as_str());
        toml::from_str(&contents).expect("failed to parse config")
    }
}
