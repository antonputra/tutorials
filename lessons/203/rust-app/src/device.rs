use std::borrow::Cow;

use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct Device<'a> {
    pub uuid: Uuid,
    pub mac: Cow<'a, str>,
    pub firmware: Cow<'a, str>,
}
