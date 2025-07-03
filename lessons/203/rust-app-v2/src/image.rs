use std::time::Instant;

use anyhow::{Context, Error};
use aws_sdk_s3::primitives::ByteStream;
use chrono::offset::Utc;
use chrono::NaiveDateTime;
use deadpool_postgres::Client;
use uuid::Uuid;

use crate::metrics::{METRICS_NAME, OP_LABEL};
use crate::state::AppState;

const OP_S3: &str = "s3";
const OP_DB: &str = "db";

pub struct Image {
    pub uuid: Uuid,
    pub created_at: NaiveDateTime,
    pub key: String,
}

impl Image {
    pub fn generate() -> Self {
        let uuid = Uuid::new_v4();
        let key = format!("rust-thumbnail-{}.png", uuid);

        Self {
            uuid,
            created_at: Utc::now().naive_local(),
            key,
        }
    }

    // Uploads the image to S3.
    pub async fn upload(&self, state: &AppState) -> Result<(), Error> {
        // Start a timer to measure the time taken to upload the image.
        let start = Instant::now();

        // Read the file from the local file system.
        let body = ByteStream::from_path(&state.config.s3.img_path)
            .await
            .context("failed to read image file")?;

        // Upload the file to the S3 bucket.
        state
            .s3_client
            .put_object()
            .bucket(&state.config.s3.bucket)
            .key(&self.key)
            .body(body)
            .send()
            .await
            .context("failed to upload image to S3")?;

        // Record the duration of the operation.
        let duration = start.elapsed().as_secs_f64();
        metrics::histogram!(METRICS_NAME, OP_LABEL => OP_S3).record(duration);

        Ok(())
    }

    /// Inserts a newly generated image into the Postgres database.
    pub async fn save(&self, state: &AppState) -> Result<(), Error> {
        // Start a timer to measure the time taken to save the image metadata.
        let start = Instant::now();

        // Get a connection from the database pool.
        let client: Client = state
            .db_pool
            .get()
            .await
            .context("failed to get database connection")?;

        // Prepare the SQL query.
        let query = "INSERT INTO rust_image VALUES ($1, $2, $3)";
        let stmt = client
            .prepare_cached(query)
            .await
            .context("failed to prepare query")?;

        // Insert the record into the database.
        client
            .execute(&stmt, &[&self.uuid, &self.key, &self.created_at])
            .await
            .context("failed to execute query")?;

        // Record the duration of the operation.
        let duration = start.elapsed().as_secs_f64();
        metrics::histogram!(METRICS_NAME, OP_LABEL => OP_DB).record(duration);

        Ok(())
    }
}
