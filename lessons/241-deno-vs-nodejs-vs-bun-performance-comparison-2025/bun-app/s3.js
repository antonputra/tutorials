import config from "./config.js";
import { S3Client } from "bun";

// https://bun.sh/docs/api/s3
const s3Client = new S3Client({
  accessKeyId: config.s3.accessKeyId,
  secretAccessKey: config.s3.secretAccessKey,
  bucket: config.s3.bucket,
  endpoint: config.s3.endpoint,
});

export default s3Client;
