mod routes;

#[macro_use]
extern crate rocket;

use self::routes::devices;
use self::routes::health;

#[launch]
fn rocket() -> _ {
    rocket::build()
        .mount("/", routes![health])
        .mount("/api", routes![devices])
}
