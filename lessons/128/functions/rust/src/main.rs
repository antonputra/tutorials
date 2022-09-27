use aws_config::SdkConfig;
use aws_sdk_dynamodb::{error::PutItemError, model::AttributeValue, types::SdkError};
use aws_sdk_s3::error::GetObjectError;
use aws_smithy_http::byte_stream;
use aws_smithy_types_convert::date_time::DateTimeExt;
use chrono::{Duration, Utc};
use lambda_http::{run, service_fn, Body, Request, Response};
use rand::Rng;
use std::env;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error(transparent)]
    PutItem(#[from] SdkError<PutItemError>),
    #[error(transparent)]
    GetObject(#[from] SdkError<GetObjectError>),
    #[error(transparent)]
    ByteStream(#[from] byte_stream::Error),
    #[error(transparent)]
    Http(#[from] lambda_http::http::Error),
    #[error(transparent)]
    Lambda(#[from] lambda_http::Error),
}

async fn function_handler(_event: Request) -> Result<Response<Body>, Error> {
    let bucket = env::var("BUCKET_NAME").expect("failed to get env");
    let key = "thumbnail.png";
    let table_name = "images";
    let config = aws_config::load_from_env().await;

    if let Some(modified) = get_s3_object(&bucket, &key, &config).await? {
        let date = get_new_date(modified);
        save_last_modified(&table_name, &date.to_string(), &config).await?;
    }

    let resp = Response::builder()
        .status(200)
        .header("content-type", "application/json")
        .body("OK".into())?;

    Ok(resp)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .with_target(false)
        .without_time()
        .init();

    run(service_fn(function_handler)).await?;

    Ok(())
}

// Downloads S3 object and returns last modified date in UTC format.
async fn get_s3_object(
    bucket: &str,
    key: &str,
    config: &SdkConfig,
) -> Result<Option<chrono::DateTime<Utc>>, Error> {
    let client = aws_sdk_s3::Client::new(config);

    let object = client.get_object().bucket(bucket).key(key).send().await?;

    if let Some(last_modified) = object.last_modified() {
        Ok(Some(last_modified.to_chrono_utc()))
    } else {
        Ok(None)
    }
}

// Saves the last modified date to the DynamoDB table.
async fn save_last_modified(
    table_name: &str,
    date: &str,
    config: &SdkConfig,
) -> Result<(), SdkError<PutItemError>> {
    let client = aws_sdk_dynamodb::Client::new(config);
    let date = AttributeValue::S(date.into());

    client
        .put_item()
        .table_name(table_name)
        .item("last_modified_date", date)
        .send()
        .await?;

    Ok(())
}

// Generates new random date.
fn get_new_date(date: chrono::DateTime<Utc>) -> chrono::DateTime<Utc> {
    let random_number_of_days = rand::thread_rng().gen_range(1..=10000) * 60 * 60 * 24;
    let duration = Duration::days(random_number_of_days);
    date.checked_add_signed(duration).unwrap()
}
