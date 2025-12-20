import sql from "./db.ts";
import type { User } from "./types.ts";

export async function save({
  name,
  address,
  phone,
  image,
  createdAt,
  updatedAt,
}: User): Promise<any> {
  return sql`INSERT INTO bun_app (name, address, phone, image, created_at, updated_at) VALUES (${name}, ${address}, ${phone}, ${image}, ${createdAt}, ${updatedAt}) RETURNING id;`;
}
