import sql from "./db.ts";
import type { User } from "./types.ts";

export async function save(user: User): Promise<[{ id: number }]> {
  return sql`INSERT INTO bun_app (name, address, phone, image, created_at, updated_at) VALUES (${user.name}, ${user.address}, ${user.phone}, ${user.image}, ${user.createdAt}, ${user.updatedAt}) RETURNING id;`;
}
