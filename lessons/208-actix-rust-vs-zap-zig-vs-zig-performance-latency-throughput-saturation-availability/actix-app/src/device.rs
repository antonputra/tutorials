use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device<'a> {
    pub id: i32,
    pub mac: &'a str,
    pub firmware: &'a str,
}
