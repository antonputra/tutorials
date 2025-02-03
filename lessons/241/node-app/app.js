import histogram from "./metrics.js";
import { save, upload } from "./users.js";
import { register } from "prom-client";
import config from "./config.js";

import * as http from "node:http";

// Timeout in milliseconds
const server = http.createServer({ keepAliveTimeout: 60000 }, (req, res) => {
  if (req.url === "/metrics") {
    res.writeHead(200, { "Content-Type": register.contentType });
    register.metrics().then((data) => res.end(data));
    return;
  }

  if (req.url === "/healthz") {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("OK");
    return;
  }

  if (req.method === "GET" && req.url === "/api/users") {
    const users = [
      {
        id: 1,
        name: "David D. Patton",
        address: "1670 Stiles Street",
        phone: "412-578-3857",
        image: "user-123.png",
        created_at: "2024-05-28T15:21:51.137Z",
        updated_at: "2024-05-28T15:21:51.137Z",
      },
      {
        id: 2,
        name: "Gary E. Eaton",
        address: "828 Collins Avenue",
        phone: "614-866-1660",
        image: "user-124.png",
        created_at: "2022-05-22T15:21:51.137Z",
        updated_at: "2024-02-22T15:21:51.137Z",
      },
      {
        id: 3,
        name: "John J. Fox",
        address: "1895 Columbia Mine Road",
        phone: "304-505-3622",
        image: "user-125.png",
        created_at: "2024-06-28T15:21:51.137Z",
        updated_at: "2024-06-28T15:21:51.137Z",
      },
    ];

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(users));
    return;
  }

  if (req.method === "POST" && req.url === "/api/users") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk.toString();
    });

    req.on("end", () => {
      let user = JSON.parse(body);
      let datetime = new Date();

      const key = `user-node-${Date.now()}.png`;

      user.createdAt = datetime;
      user.updatedAt = datetime;
      user.image = key;

      const end = histogram.startTimer();
      save(user)
        .then((record) => {
          end({ op: "db" });
          user.id = record[0].id;

          res.writeHead(201, { "Content-Type": "application/json" });
          res.end(JSON.stringify(user));
        })
        .catch((error) => {
          console.error(error);

          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ message: error.message }));
        });
    });

    return;
  }

  res.writeHead(404, { "Content-Type": "text/plain" });
  res.end("Not Found");
});

console.log(`Node is listening on http://0.0.0.0:${config.appPort} ...`);

server.listen(config.appPort);
