use ntex::web::{self, App};
use routes::{devices, health};

mod device;
mod routes;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[ntex::main]
async fn main() -> std::io::Result<()> {
    web::server(|| App::new().service((health, devices)))
        .bind("0.0.0.0:8080")?
        .run()
        .await
}
