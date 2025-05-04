import { sql, s3, write } from "bun";
import { readFile } from "node:fs/promises";
import s3Client from "./s3";

export async function save({
  name,
  address,
  phone,
  image,
  createdAt,
  updatedAt,
}) {
  return sql`INSERT INTO bun_user (name, address, phone, image, created_at, updated_at) VALUES (${name}, ${address}, ${phone}, ${image}, ${createdAt}, ${updatedAt}) RETURNING id;`;
}

export async function upload(key, filePath) {
  const metadata = s3Client.file(key);

  return write(metadata, await readFile(filePath));
}
