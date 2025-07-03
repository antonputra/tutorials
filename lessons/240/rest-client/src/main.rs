use reqwest::{Client, Response};
use serde::{Deserialize, Serialize};
use std::time::Duration;

const URI: &str = "http://localhost:8080/api/devices";
const TIMEOUT: u64 = 20000;
const REQUEST: &str = "POST";

#[derive(Debug, Serialize, Deserialize)]
pub struct Device<'a> {
    pub mac: &'a str,
    pub firmware: &'a str,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::builder().build()?;

    let response: Response;

    if REQUEST == "GET" {
        response = client
            .get(URI)
            .timeout(Duration::from_millis(TIMEOUT))
            .send()
            .await?;
    } else {
        let device = Device {
            mac: "EF-2B-C4-F5-D6-34",
            firmware: "2.1.5",
        };
        response = client
            .post(URI)
            .json(&device)
            .timeout(Duration::from_millis(TIMEOUT))
            .send()
            .await?;
    }

    let body = response.bytes().await?;

    println!("{:?}", body);

    Ok(())
}
