use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device {
    pub uuid: String,
    pub mac: String,
    pub firmware: String,
}
