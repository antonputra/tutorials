import { PutObjectCommand } from "npm:@aws-sdk/client-s3";
import { readFile } from "node:fs/promises";

import sql from "./db.js";
import s3Client from "./s3.js";

export async function save({
  name,
  address,
  phone,
  image,
  createdAt,
  updatedAt,
}) {
  return sql`INSERT INTO deno_user (name, address, phone, image, created_at, updated_at) VALUES (${name}, ${address}, ${phone}, ${image}, ${createdAt}, ${updatedAt}) RETURNING id;`;
}

export async function upload(bucketName, key, filePath) {
  const command = new PutObjectCommand({
    Bucket: bucketName,
    Key: key,
    Body: await readFile(filePath),
  });
  return s3Client.send(command);
}
