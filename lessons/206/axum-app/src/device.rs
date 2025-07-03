use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device {
    pub id: i32,
    pub mac: String,
    pub firmware: String,
}
