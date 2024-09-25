import summary from "./metrics.js";
import save from "./devices.js";
import { randomUUID } from "crypto";
import { register } from "prom-client";
import config from "./config.js";

import * as http from "node:http";

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
    const device = {
      uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
      mac: "5F-33-CC-1F-43-82",
      firmware: "2.1.6",
    };

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

      device.uuid = randomUUID();

      const end = summary.startTimer();

      save(device)
        .then(() => {
          end({ op: "db" });

          res.writeHead(201, { "Content-Type": "application/json" });
          res.end(JSON.stringify(device));
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

server.listen(config.appPort);
