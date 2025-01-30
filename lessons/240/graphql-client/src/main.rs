use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

const URI: &str = "http://localhost:8080/query";
const TIMEOUT: u64 = 20000;
const REQUEST: &str = "GET";

#[derive(Debug, Serialize, Deserialize)]
pub struct GraphQLRequest<'a> {
    pub query: &'a str,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::builder().build()?;

    let req: GraphQLRequest;

    if REQUEST == "GET" {
        req = GraphQLRequest {
            query: "query {device {id uuid mac firmware createdAt updatedAt}}",
        }
    } else {
        req = GraphQLRequest {
            query: "mutation {createDevice(input: {mac: \"81-6E-79-DA-5A-B2\", firmware: \"4.0.2\"}) {id uuid mac firmware createdAt updatedAt}}",
        }
    }

    let response = client
        .post(URI)
        .json(&req)
        .timeout(Duration::from_millis(TIMEOUT))
        .send()
        .await?;

    let body = response.bytes().await?;

    println!("{:?}", body);

    Ok(())
}
