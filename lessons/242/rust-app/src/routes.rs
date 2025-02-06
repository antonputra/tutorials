use crate::device::Device;
use serde_json;
use std::io::BufWriter;
use std::{
    io::{prelude::*, BufReader},
    net::TcpStream,
};

pub fn get_devices() -> (u16, String, usize) {
    let devices = [
        Device {
            id: 1,
            uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
            mac: "EF-2B-C4-F5-D6-34",
            firmware: "2.1.5",
            created_at: "2024-05-28T15:21:51.137Z",
            updated_at: "2024-05-28T15:21:51.137Z",
        },
        Device {
            id: 2,
            uuid: "d2293412-36eb-46e7-9231-af7e9249fffe",
            mac: "E7-34-96-33-0C-4C",
            firmware: "1.0.3",
            created_at: "2024-01-28T15:20:51.137Z",
            updated_at: "2024-01-28T15:20:51.137Z",
        },
        Device {
            id: 3,
            uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
            mac: "68-93-9B-B5-33-B9",
            firmware: "4.3.1",
            created_at: "2024-08-28T15:18:21.137Z",
            updated_at: "2024-08-28T15:18:21.137Z",
        },
        Device {
            id: 4,
            uuid: "ab4efcd0-f542-4944-9dd9-0ad844dfcbd3",
            mac: "E7-6F-69-99-F1-ED",
            firmware: "6.2.0",
            created_at: "2024-08-29T15:18:21.137Z",
            updated_at: "2024-08-29T15:18:21.137Z",
        },
        Device {
            id: 5,
            uuid: "9e725cbc-2c4e-446c-a274-962531f90927",
            mac: "9F-57-E5-1F-F5-6B",
            firmware: "0.6.4",
            created_at: "2024-18-28T15:18:21.137Z",
            updated_at: "2024-18-28T15:18:21.137Z",
        },
    ];

    let body = serde_json::to_string(&devices).unwrap();
    let length = body.len();

    (200, body, length)
}

pub fn not_found() -> (u16, String, usize) {
    let body = serde_json::to_string("Not Found").unwrap();
    let length = body.len();

    (404, body, length)
}

pub fn handle_connection(stream: TcpStream) {
    let mut input = BufReader::new(&stream).lines();
    let mut output = BufWriter::new(&stream);

    let mut keep_alive = true;
    while keep_alive {
        if let Some(request_line) = input.next() {
            match request_line {
                Ok(line) => {
                    keep_alive = false;
                    while let Some(header) = input.next() {
                        let Ok(header) = header else {
                            println!("Error reading header line");
                            break;
                        };

                        if header.is_empty() {
                            break;
                        }

                        if !keep_alive && header.ends_with("keep-alive") {
                            keep_alive = true;
                        }
                    }

                    let (status, body, length) = match &line[..] {
                        "GET /api/devices HTTP/1.1" => get_devices(),
                        _ => not_found(),
                    };

                    if let Err(e) =
                        write!(output, "HTTP/1.1 {status}\r\nContent-Length: {length}\r\n")
                            .and_then(|_| {
                                if keep_alive {
                                    write!(output, "Connection: keep-alive\r\n")
                                } else {
                                    write!(output, "Connection: close\r\n")
                                }
                            })
                            .and_then(|_| write!(output, "\r\n{body}"))
                            .and_then(|_| output.flush())
                    {
                        println!("Failed to write response: {e}");
                        break;
                    }
                }
                Err(e) => {
                    print!("Failed to read request line: {:?}", e);
                    break;
                }
            }
        }
    }
}
