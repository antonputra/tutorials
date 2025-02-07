use std::io::{self, BufWriter};
use std::sync::Arc;
use std::{
    io::{prelude::*, BufReader},
    net::TcpStream,
};

pub fn handle_connection(
    stream: TcpStream,
    max_requests_per_connection: usize,
    ok: Arc<String>,
    not_found: Arc<String>,
) -> io::Result<()> {
    let mut input = BufReader::new(&stream).lines();
    let mut output = BufWriter::new(&stream);

    let mut requests_processed = 0;
    let mut keep_alive = true;

    while keep_alive {
        let line = match input.next() {
            Some(v) => v,
            None => return Ok(()),
        };
        let line = line?;
        requests_processed += 1;

        keep_alive = false;
        let header = if let Some(v) = input.next() {
            v
        } else {
            return Ok(());
        }?;
        if !keep_alive && header.ends_with("keep-alive") {
            keep_alive = requests_processed <= max_requests_per_connection;
        }
        let (res, status) = match line.as_str() {
            "GET /api/devices HTTP/1.1" => (ok.clone(), b"200"),
            _ => (not_found.clone(), b"404"),
        };
        output.write_all(b"HTTP/1.1 ")?;
        output.write_all(status)?;

        output.write_all(b"\r\nContent-Length: ")?;
        output.write_all(res.len().to_string().as_bytes())?;
        output.write_all(b"\r\n")?;

        if keep_alive {
            output.write_all(b"Connection: keep-alive\r\n")?;
        } else {
            output.write_all(b"Connection: close\r\n")?;
        }
        output.write_all(b"\r\n")?;
        output.write_all(res.as_bytes())?;
        output.flush()?;
    }
    Ok(())
}
