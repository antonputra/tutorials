use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize)]
pub struct Device<'a> {
    pub id: i32,
    #[serde(flatten)]
    pub data: DeviceData<'a>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeviceData<'a> {
    pub mac: &'a str,
    pub firmware: &'a str,
}
