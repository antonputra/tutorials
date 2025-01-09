import histogram from "./metrics.js";
import save from "./devices.js";
import { randomUUID } from "crypto";
import { register } from "prom-client";
import config from "./config.js";
import memcached from "./cache.js";

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

  if (req.method === "GET" && req.url === "/api/devices") {
    const device = [
      {
        id: 1,
        uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
        mac: "EF-2B-C4-F5-D6-34",
        firmware: "2.1.5",
        created_at: "2024-05-28T15:21:51.137Z",
        updated_at: "2024-05-28T15:21:51.137Z",
      },
      {
        id: 2,
        uuid: "d2293412-36eb-46e7-9231-af7e9249fffe",
        mac: "E7-34-96-33-0C-4C",
        firmware: "1.0.3",
        created_at: "2024-01-28T15:20:51.137Z",
        updated_at: "2024-01-28T15:20:51.137Z",
      },
      {
        id: 3,
        uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
        mac: "68-93-9B-B5-33-B9",
        firmware: "4.3.1",
        created_at: "2024-08-28T15:18:21.137Z",
        updated_at: "2024-08-28T15:18:21.137Z",
      },
    ];

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(device));
    return;
  }

  if (req.method === "POST" && req.url === "/api/devices") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk.toString();
    });

    req.on("end", () => {
      let device = JSON.parse(body);
      let datetime = new Date();

      device.uuid = randomUUID();
      device.createdAt = datetime;
      device.updatedAt = datetime;

      const dbTimer = histogram.startTimer();
      save(device)
        .then((result) => {
          dbTimer({ op: "insert" });
          device.id = result[0].id;

          const cacheTimer = histogram.startTimer();
          memcached.set(device.uuid, device, 20, (error) => {
            if (error) {
              console.error(error);
              res.writeHead(400, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ message: error.message }));
            }
            cacheTimer({ op: "set" });
            res.writeHead(201, { "Content-Type": "application/json" });
            res.end(JSON.stringify(device));
          });
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
