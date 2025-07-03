fn main() {
    __impl::main();
}

#[cfg(not(unix))]
mod __impl {
    pub fn main() {
        println!("This example only works on unix");
    }
}

#[cfg(unix)]
mod __impl {
    #[global_allocator]
    static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

    use std::io::BufRead;
    use std::sync::Arc;
    use std::{env, io};

    use may_minihttp::{HttpService, HttpServiceFactory, Request, Response};
    use may_postgres::{Client, Statement};
    use serde::Deserialize;
    use yarte::Serialize;

    #[derive(Deserialize)]
    pub struct InputDevice<'a> {
        pub mac: &'a str,
        pub firmware: &'a str,
    }

    #[derive(Serialize)]
    pub struct Device<'a> {
        pub id: i32,
        pub mac: &'a str,
        pub firmware: &'a str,
    }

    const fn get_devices<'a>() -> [Device<'a>; 5] {
        [
            Device {
                id: 0,
                mac: "5F-33-CC-1F-43-82",
                firmware: "2.1.6",
            },
            Device {
                id: 1,
                mac: "44-39-34-5E-9C-F2",
                firmware: "3.0.1",
            },
            Device {
                id: 2,
                mac: "2B-6E-79-C7-22-1B",
                firmware: "1.8.9",
            },
            Device {
                id: 3,
                mac: "06-0A-79-47-18-E1",
                firmware: "4.0.9",
            },
            Device {
                id: 4,
                mac: "68-32-8F-00-B6-F4",
                firmware: "5.0.0",
            },
        ]
    }

    struct PgConnectionPool {
        clients: Vec<PgConnection>,
    }

    impl PgConnectionPool {
        fn new(db_url: &'static str) -> PgConnectionPool {
            let size = num_cpus::get();
            let clients = (0..size)
                .map(|_| may::go!(move || PgConnection::new(db_url)))
                .collect::<Vec<_>>();
            let mut clients: Vec<_> = clients.into_iter().map(|t| t.join().unwrap()).collect();
            clients.sort_by(|a, b| (a.client.id() % size).cmp(&(b.client.id() % size)));
            PgConnectionPool { clients }
        }

        fn get_connection(&self, id: usize) -> PgConnection {
            let len = self.clients.len();
            let connection = &self.clients[id % len];
            assert_eq!(connection.client.id() % len, id % len);
            PgConnection {
                client: connection.client.clone(),
                update: connection.update.clone(),
            }
        }
    }

    struct PgConnection {
        client: Client,
        update: Arc<Statement>,
    }

    impl PgConnection {
        fn new(db_url: &str) -> Self {
            let client = may_postgres::connect(db_url).unwrap();

            let update = client
                .prepare("INSERT INTO rust_device (mac, firmware) VALUES ($1, $2) RETURNING id")
                .unwrap();
            let update = Arc::new(update);

            PgConnection { client, update }
        }

        fn insert_device<'a>(
            &self,
            mac: &'a str,
            firmware: &'a str,
        ) -> Result<Device<'a>, may_postgres::Error> {
            let mut stream = self
                .client
                .query_raw(self.update.as_ref(), &[&mac, &firmware])?;
            let row = match stream.next().transpose()? {
                Some(row) => row,
                None => unreachable!(),
            };
            Ok(Device {
                id: row.get(0),
                mac,
                firmware,
            })
        }
    }

    struct TutorialTest {
        db: PgConnection,
    }

    impl HttpService for TutorialTest {
        fn call(&mut self, req: Request, rsp: &mut Response) -> io::Result<()> {
            match req.path() {
                "/healthz" => {
                    rsp.header("Content-Type: text/plain").body("OK");
                }
                "/api/devices" => match req.method() {
                    "GET" => {
                        rsp.header("Content-Type: application/json");
                        let devices = get_devices();
                        devices.to_bytes_mut(rsp.body_mut());
                    }
                    "POST" => {
                        rsp.header("Content-Type: application/json");
                        let mut body = req.body();
                        let buf = match body.fill_buf() {
                            Ok(buf) => buf,
                            Err(_) => {
                                rsp.status_code(500, "Internal error");
                                return Ok(());
                            }
                        };
                        let input: InputDevice = match serde_json::from_slice(buf) {
                            Ok(input) => input,
                            Err(_) => {
                                rsp.status_code(500, "Internal error");
                                return Ok(());
                            }
                        };

                        let device = self.db.insert_device(input.mac, input.firmware);
                        match device {
                            Ok(device) => {
                                device.to_bytes_mut(rsp.body_mut());
                            }
                            Err(_) => {
                                rsp.status_code(500, "Internal error");
                                return Ok(());
                            }
                        }
                    }
                    &_ => {
                        rsp.status_code(404, "Not Found");
                    }
                },
                _ => {
                    rsp.status_code(404, "Not Found");
                }
            }

            Ok(())
        }
    }

    struct HttpServer {
        db_pool: PgConnectionPool,
    }

    impl HttpServiceFactory for HttpServer {
        type Service = TutorialTest;

        fn new_service(&self, id: usize) -> Self::Service {
            let db = self.db_pool.get_connection(id);
            TutorialTest { db }
        }
    }

    pub fn main() {
        let host = env::var("POSTGRES_HOST").expect("The `POSTGRES_HOST` env variable is missing");
        let user = env::var("POSTGRES_USER").expect("The `POSTGRES_USER` env variable is missing");
        let pwd = env::var("POSTGRES_PWD").expect("The `POSTGRES_PWD` env variable is missing");
        let db = env::var("POSTGRES_DB").expect("The `POSTGRES_DB` env variable is missing");

        may::config()
            .set_pool_capacity(10000)
            .set_stack_size(0x1000);

        let connect_str = Box::leak(
            format!("postgresql://{}:{}@{}:5432/{}", user, pwd, host, db).into_boxed_str(),
        );
        let server = HttpServer {
            db_pool: PgConnectionPool::new(connect_str),
        };

        println!("Starting http server: 0.0.0.0:8080");
        server.start("0.0.0.0:8080").unwrap().join().unwrap();
    }
}
