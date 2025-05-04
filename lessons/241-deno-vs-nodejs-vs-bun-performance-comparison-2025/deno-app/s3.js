import { S3Client } from "npm:@aws-sdk/client-s3";
import config from "./config.js";

const s3Client = new S3Client({
  region: config.s3.region,
  forcePathStyle: true,
  endpoint: config.s3.endpoint,
  credentials: {
    accessKeyId: config.s3.accessKeyId,
    secretAccessKey: config.s3.secretAccessKey,
  },
});

export default s3Client;
