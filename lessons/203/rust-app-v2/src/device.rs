use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device<'a> {
    pub uuid: &'a str,
    pub mac: &'a str,
    pub firmware: &'a str,
}
