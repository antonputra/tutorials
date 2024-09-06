use std::borrow::Cow;

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Device<'a> {
    pub uuid: Cow<'a, str>,
    pub mac: Cow<'a, str>,
    pub firmware: Cow<'a, str>,
}
