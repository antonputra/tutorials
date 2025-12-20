import config from "./config.ts";
import { save } from "./users.ts";
import type { User } from "./types.ts";
import type { Config } from "./config.ts";


const server = Bun.serve({
  // Timeout in seconds to match Node.js
  idleTimeout: 60,
  development: false,
  reusePort: true,
  port: (config as Config).appPort,
  async fetch(req: Request): Promise<Response> {
    const path = new URL(req.url).pathname;
    if (path === "/healthz") return new Response("OK");

    if (req.method === "GET" && path === "/api/users") {
      const users: User[] = [
        {
          id: 1,
          name: "David D. Patton",
          address: "1670 Stiles Street",
          phone: "412-578-3857",
          image: `user.png`,
        },
        {
          id: 2,
          name: "Gary E. Eaton",
          address: "828 Collins Avenue",
          phone: "614-866-1660",
          image: `user.png`,
        },
        {
          id: 3,
          name: "John J. Fox",
          address: "1895 Columbia Mine Road",
          phone: "304-505-3622",
          image: `user.png`,
        },
      ];
      return Response.json(users);
    }

    if (req.method === "POST" && path === "/api/users") {
      const incomingUser: any = await req.json();
      const datetime = new Date();
      const key = `user-bun-${datetime.getTime()}.png`;
      const user: User = {
        ...incomingUser,
        createdAt: datetime,
        updatedAt: datetime,
        image: key,
      };

      return save(user)
        .then((record: [{ id: number }]) => {
          user.id = record[0].id;
          return Response.json(user, { status: 201 });
        })
        .catch((error: Error) => {
          console.error(error);
          return Response.json({ message: error.message }, { status: 400 });
        });
    }
    return new Response("Resource not found", { status: 404 });
  },
});

console.log(`Bun is listening on http://0.0.0.0:${server.port} ...`);
