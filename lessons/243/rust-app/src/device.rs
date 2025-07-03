use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device<'a> {
    pub id: i32,
    pub uuid: &'a str,
    pub mac: &'a str,
    pub firmware: &'a str,
    pub created_at: &'a str,
    pub updated_at: &'a str,
}
