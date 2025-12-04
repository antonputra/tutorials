import sql from "./db.js";

export async function save({
  name,
  address,
  phone,
  image,
  createdAt,
  updatedAt,
}) {
  return sql`INSERT INTO node_user (name, address, phone, image, created_at, updated_at) VALUES (${name}, ${address}, ${phone}, ${image}, ${createdAt}, ${updatedAt}) RETURNING id;`;
}
