mod device;
mod job;
mod routes;
mod thread_pool;
mod worker;

use crate::routes::handle_connection;
use crate::thread_pool::ThreadPool;

use std::net::TcpListener;

const PORT: i16 = 8080;

fn main() {
    let mode = std::env::var("MODE").expect("The `MODE` env variable is missing");

    let addr = format!("0.0.0.0:{}", PORT);
    let listener = TcpListener::bind(addr).unwrap();

    match mode.as_str() {
        "SINGLE" => {
            println!("Starting a web server in single-threaded mode.");
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => handle_connection(stream),
                    Err(err) => print!("{:?}", err),
                }
            }
        }
        "MULTI" => {
            let thread_count =
                std::env::var("THREAD_COUNT").expect("The `THREAD_COUNT` env variable is missing");
            let pool = ThreadPool::new(thread_count.parse::<usize>().unwrap());

            println!(
                "Starting a web server in multi-threaded mode with {} threads.",
                thread_count
            );
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        pool.execute(|| {
                            handle_connection(stream);
                        });
                    }
                    Err(err) => print!("{:?}", err),
                }
            }
        }
        _ => panic!("\"{}\" mode is NOT supported!", mode),
    }

    println!("Shutting down.");
}
