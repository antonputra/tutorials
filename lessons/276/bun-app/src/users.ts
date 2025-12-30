import sql from "./db.ts";
import type { User } from "./types.ts";

export function save(user: User): Promise<[{ id: number }]> {
  const { name, address, phone, createdAt, updatedAt } = user;
  return sql`INSERT INTO bun_app (name, address, phone, created_at, updated_at) VALUES (${name}, ${address}, ${phone}, ${createdAt}, ${updatedAt}) RETURNING id;`;
}
