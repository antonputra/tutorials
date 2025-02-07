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

    // The job & its connection will be terminated after this amount of requests inorder to give
    // a chance to requests pending in the queue. This approach is not ideal and will ork only is
    // test scenarios such as Jmeter (i.e. it's not suitable for productive usage),
    // but is very simple to implement in order to demonstrate the performance benefits of
    // keep-alive.
    //
    // Larger value will lead to higher latency. Smaller value will lead to worse throughout.
    let max_req = std::env::var("MAX_REQUEST").unwrap_or_else(|_| "200".to_owned());
    let max_req = max_req
        .parse::<usize>()
        .expect("The `MAX_REQUEST` env variable is invalid");

    let addr = format!("0.0.0.0:{}", PORT);
    let listener = TcpListener::bind(addr).unwrap();
    match mode.as_str() {
        "SINGLE" => {
            println!("Starting a web server in single-threaded mode.");
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        if let Err(err) = handle_connection(stream, max_req) {
                            eprintln!("{}", err);
                        }
                    }
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
                        pool.execute(move || {
                            if let Err(err) = handle_connection(stream, max_req) {
                                eprintln!("{}", err);
                            }
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
