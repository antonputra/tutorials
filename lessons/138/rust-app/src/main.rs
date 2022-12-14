#[macro_use] extern crate rocket;
use rocket::serde::json::Json;
use rocket::serde::{Serialize, Deserialize};
use rocket::response::status;

#[derive(Serialize, Deserialize)]
#[serde(crate = "rocket::serde")]
struct Device {
    id: i32,
    mac: String,
    firmware: String,
}

fn fibonacci(n: u32) -> u32 {
    match n {
        1 | 2 => 1,
        3 => 2,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

#[get("/devices")]
fn get_devices() -> Json<Vec<Device>> {
    let mut devices = Vec::new();

    devices.push(Device {id: 1, mac: String::from("5F-33-CC-1F-43-82"), firmware: String::from("2.1.6")});
    devices.push(Device {id: 2, mac: String::from("EF-2B-C4-F5-D6-34"), firmware: String::from("2.1.6")});

    Json(devices)
}

#[post("/devices")]
fn create_device() -> status::Created<String> {
    let number = 40;

    let fib = fibonacci(number);
    let location = format!("/devices/{}", fib);
    
    status::Created::new(location)
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/api/", routes![get_devices, create_device])
}
