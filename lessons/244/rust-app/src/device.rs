use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device {
    pub id: Option<i32>,
    pub mac: String,
    pub firmware: String,
}
