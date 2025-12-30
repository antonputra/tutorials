import config from "./config.ts";
import { save } from "./users.ts";
import type { User, Device } from "./types.ts";

const server = Bun.serve({
  // Timeout in seconds to match Node.js
  idleTimeout: 60,
  development: false,
  reusePort: true,
  port: config.appPort,
  async fetch(req: Request): Promise<Response> {
    const path = new URL(req.url).pathname;

    if (path === "/healthz") return new Response("OK", { status: 200 });

    if (path === "/api/devices") {
      if (req.method === "GET") {
        const devices: Device[] = [
          { uuid: Bun.randomUUIDv7(), mac: "5F-33-CC-1F-43-82", firmware: "2.1.6" },
          { uuid: Bun.randomUUIDv7(), mac: "EF-2B-C4-F5-D6-34", firmware: "2.1.5" },
          { uuid: Bun.randomUUIDv7(), mac: "62-46-13-B7-B3-A1", firmware: "3.0.0" },
        ];
        return Response.json(devices);
      }
    }

    if (path === "/api/users") {
      if (req.method === "POST") {
        const incomingUser = await req.json() as User;
        const now = Date.now();
        const datetime = new Date(now);

        const user: User = {
          name: incomingUser.name,
          address: incomingUser.address,
          phone: incomingUser.phone,
          createdAt: datetime,
          updatedAt: datetime,
        };

        try {
          const record = await save(user);
          user.id = record[0].id;
          return Response.json(user, { status: 201 });
        } catch (error: unknown) {
          return Response.json({ message: (error as Error).message }, { status: 400 });
        }
      }
    }

    return new Response("Resource not found", { status: 404 });
  },
});

console.log(`Bun is listening on http://0.0.0.0:${server.port} ...`);
