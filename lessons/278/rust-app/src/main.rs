use actix_web::{App, HttpRequest, HttpServer, web};

async fn hello(_req: HttpRequest) -> &'static str {
    "Hello, world!"
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().service(web::resource("/hello").to(hello)))
        .bind(("0.0.0.0", 8080))?
        .workers(2)
        .run()
        .await
}
