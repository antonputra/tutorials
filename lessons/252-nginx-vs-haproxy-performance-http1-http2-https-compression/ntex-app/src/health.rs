use ntex::http::Response;
use ntex::web::Responder;

pub async fn health() -> impl Responder {
    Response::Ok().finish()
}
