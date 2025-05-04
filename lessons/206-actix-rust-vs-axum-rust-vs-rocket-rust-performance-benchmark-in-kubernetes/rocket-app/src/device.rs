use rocket::serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
#[serde(crate = "rocket::serde")]
pub struct Device {
    pub id: i32,
    pub mac: String,
    pub firmware: String,
}
