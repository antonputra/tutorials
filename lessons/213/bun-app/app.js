import { randomUUID } from "crypto";
import config from "./config.js";
import save from "./devices.js";
import histogram from "./metrics.js";
import { register } from "prom-client";

const server = Bun.serve({
  idleTimeout: 60,
  port: config.appPort,
  async fetch(req) {
    const path = new URL(req.url).pathname;

    if (path === "/healthz") return new Response("OK");

    if (path === "/metrics")
      return register.metrics().then((data) => new Response(data));

    if (req.method === "GET" && path === "/api/devices") {
      const device = {
        uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
        mac: "5F-33-CC-1F-43-82",
        firmware: "2.1.6",
      };

      return Response.json(device);
    }

    if (req.method === "POST" && path === "/api/devices") {
      let device = await req.json();
      device.uuid = randomUUID();

      const end = histogram.startTimer();
      return save(device)
        .then(() => {
          end({ op: "db" });

          return Response.json(device, { status: 201 });
        })
        .catch((error) => {
          console.error(error);

          return Response.json({ message: error.message }, { status: 400 });
        });
    }

    return new Response("Resource not found", { status: 404 });
  },
});

console.log(`Bun is listening on http://0.0.0.0:${server.port} ...`);
