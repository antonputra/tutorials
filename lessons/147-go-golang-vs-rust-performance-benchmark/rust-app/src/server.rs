use std::env;

use tonic::{
    transport::{Identity, Server, ServerTlsConfig},
    Request, Response, Status,
};

use hardware::manager_server::{Manager, ManagerServer};
use hardware::{Device, DeviceRequest};

pub mod hardware {
    tonic::include_proto!("hardware");
}

#[derive(Debug, Default)]
pub struct MyManager {}

#[tonic::async_trait]
impl Manager for MyManager {
    async fn get_device(
        &self,
        _request: Request<DeviceRequest>,
    ) -> Result<Response<Device>, Status> {
        let reply = hardware::Device {
            uuid: String::from("a7090a19-9f08-43ce-a3e6-7bb8641ee77d"),
            mac: String::from("EF-2B-C4-F5-D6-34"),
            firmware: String::from("2.1.6"),
        };

        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let tls_enabled_string = env::var("TLS_ENABLED")?;
    let tls_enabled: bool = tls_enabled_string.parse().unwrap();

    let addr = "0.0.0.0:50050".parse()?;
    let manager = MyManager::default();

    if tls_enabled {
        println!("Starting gRPC server WITH TLS...");

        let cert = std::fs::read_to_string("cert.pem")?;
        let key = std::fs::read_to_string("key.pem")?;

        let identity = Identity::from_pem(cert, key);

        Server::builder()
            .tls_config(ServerTlsConfig::new().identity(identity))?
            .add_service(ManagerServer::new(manager))
            .serve(addr)
            .await?;
    } else {
        println!("Starting gRPC server WITHOUT TLS...");
        Server::builder()
            .add_service(ManagerServer::new(manager))
            .serve(addr)
            .await?;
    }

    Ok(())
}
