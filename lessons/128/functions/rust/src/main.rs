use aws_config::SdkConfig;
use aws_sdk_dynamodb::model::AttributeValue;
use aws_sdk_s3::types::DateTime;
use aws_smithy_types_convert::date_time::DateTimeExt;
use chrono::Duration as OldDuration;
use chrono::Utc;
use lambda_http::{run, service_fn, Body, Error, Request, Response};
use rand::Rng;
use std::env;
use std::time::Duration;

async fn function_handler(_event: Request) -> Result<Response<Body>, Error> {
    let bucket = env::var("BUCKET_NAME").expect("failed to get env");
    let key = "thumbnail.png";
    let table_name = "images";
    let config = aws_config::load_from_env().await;

    let date = get_s3_object(&bucket, &key, &config).await;
    let date = get_new_date(date);

    save_last_modified(&table_name, &date.to_string(), &config).await;

    let resp = Response::builder()
        .status(200)
        .header("content-type", "application/json")
        .body("OK".into())
        .map_err(Box::new)?;
    Ok(resp)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .with_target(false)
        .without_time()
        .init();

    run(service_fn(function_handler)).await
}

// Downloads S3 object and returns last modified date in UTC format.
async fn get_s3_object(bucket: &str, key: &str, config: &SdkConfig) -> chrono::DateTime<Utc> {
    let client = aws_sdk_s3::Client::new(config);

    let object = client
        .get_object()
        .bucket(bucket)
        .key(key)
        .send()
        .await
        .expect("failed to fetch S3 object");

    let date = object.last_modified().expect("failed to get date");
    let date: DateTime = date.clone().into();

    object.body.collect().await.expect("failed to read body");
    date.to_chrono_utc()
}

// Saves the last modified date to the DynamoDB table.
async fn save_last_modified(table_name: &str, date: &str, config: &SdkConfig) {
    let client = aws_sdk_dynamodb::Client::new(config);
    let date = AttributeValue::S(date.into());

    client
        .put_item()
        .table_name(table_name)
        .item("last_modified_date", date)
        .send()
        .await
        .expect("failed to sate item to dynamodb");
}

// Generates new random date.
fn get_new_date(date: chrono::DateTime<Utc>) -> chrono::DateTime<Utc> {
    let random_number_of_days = rand::thread_rng().gen_range(1..=10000) * 60 * 60 * 24;

    let duration = Duration::new(random_number_of_days, 0);
    let duration = OldDuration::from_std(duration).expect("failed");
    date.checked_add_signed(duration).expect("failed")
}
