import config from "./config.ts";
import { save } from "./users.ts";
import type { User } from "./types.ts";

const server = Bun.serve({
  // Timeout in seconds to match Node.js
  idleTimeout: 60,
  development: false,
  reusePort: true,
  port: config.appPort,
  async fetch(req: Request): Promise<Response> {
    const path = new URL(req.url).pathname;

    if (path === "/healthz") return new Response("OK", { status: 200 });
    if (path === "/api/users") {
      if (req.method === "GET") {
        const users: User[] = [
          { id: 1, name: "David D. Patton", address: "1670 Stiles Street", phone: "412-578-3857", image: `user.png`, },
          { id: 2, name: "Gary E. Eaton", address: "828 Collins Avenue", phone: "614-866-1660", image: `user.png`, },
          { id: 3, name: "John J. Fox", address: "1895 Columbia Mine Road", phone: "304-505-3622", image: `user.png`, },
        ];
        return Response.json(users);
      }

      if (req.method === "POST") {
        const incomingUser = await req.json() as User;
        const now = Date.now();
        const datetime = new Date(now);

        const user: User = {
          name: incomingUser.name,
          address: incomingUser.address,
          phone: incomingUser.phone,
          image: `user-bun-${now}.png`,
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
