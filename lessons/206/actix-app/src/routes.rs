use actix_web::{get, http::header::CONTENT_TYPE, HttpResponse};

static DEVICES: &str = r#"[{"id":1,"mac":"5F-33-CC-1F-43-82","firmware":"2.1.6"},{"id":2,"mac":"EF-2B-C4-F5-D6-34","firmware":"2.1.5"},{"id":3,"mac":"62-46-13-B7-B3-A1","firmware":"3.0.0"},{"id":4,"mac":"96-A8-DE-5B-77-14","firmware":"1.0.1"},{"id":5,"mac":"7E-3B-62-A6-09-12","firmware":"3.5.6"}]"#;

// (Placeholder) Returns the status of the application.
#[get("/healthz")]
async fn health() -> HttpResponse {
    HttpResponse::Ok().body("OK")
}

/// Returns a list of connected devices.
#[get("/api/devices")]
async fn devices() -> HttpResponse {
    HttpResponse::Ok()
        .insert_header((CONTENT_TYPE, "application/json"))
        .body(DEVICES)
}
