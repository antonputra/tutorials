use chrono::offset::Utc;
use chrono::NaiveDateTime;
use uuid::Uuid;

pub struct Image {
    pub uuid: Uuid,
    pub created_at: NaiveDateTime,
    pub key: String,
}

pub fn generate_image() -> Image {
    let id = Uuid::new_v4();
    Image {
        uuid: id,
        created_at: Utc::now().naive_local(),
        key: format!("rust-thumbnail-{id}.png"),
    }
}
