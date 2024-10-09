use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device {
    pub uuid: &'static str,
    pub mac: &'static str,
    pub firmware: &'static str,
}
