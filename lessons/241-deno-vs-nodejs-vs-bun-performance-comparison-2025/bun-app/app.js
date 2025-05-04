import config from "./config.js";
import { save, upload } from "./users.js";
import histogram from "./metrics.js";
import { register } from "prom-client";

const server = Bun.serve({
  // Timeout in seconds to match Node.js
  idleTimeout: 60,
  development: false,
  reusePort: true,
  port: config.appPort,
  async fetch(req) {
    const path = new URL(req.url).pathname;

    if (path === "/healthz") return new Response("OK");

    if (path === "/metrics")
      return register.metrics().then((data) => new Response(data));

    if (req.method === "GET" && path === "/api/users") {
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

      return Response.json(users);
    }

    if (req.method === "POST" && path === "/api/users") {
      let user = await req.json();
      let datetime = new Date();

      const key = `user-bun-${Date.now()}.png`;

      user.createdAt = datetime;
      user.updatedAt = datetime;
      user.image = key;

      const end = histogram.startTimer();
      return save(user)
        .then((record) => {
          end({ op: "db" });
          user.id = record[0].id;

          return Response.json(user, { status: 201 });
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
