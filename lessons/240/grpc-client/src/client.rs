use device::cloud_client::CloudClient;
use device::{CreateDeviceRequest, DeviceRequest};

const URI: &str = "http://localhost:8080";
const REQUEST: &str = "GET";

pub mod device {
    tonic::include_proto!("device");
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = CloudClient::connect(URI).await?;

    if REQUEST == "GET" {
        let dvr = DeviceRequest {};
        let request = tonic::Request::new(dvr);
        let response = client.get_devices(request).await?;
        println!("RESPONSE={:?}", response);
    } else {
        let dvr = CreateDeviceRequest {
            mac: "81-6E-79-DA-5A-B2".into(),
            firmware: "4.0.2".into(),
        };
        let request = tonic::Request::new(dvr);
        let response = client.create_device(request).await?;
        println!("RESPONSE={:?}", response);
    }

    Ok(())
}
