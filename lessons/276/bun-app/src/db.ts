import config from "./config.ts";
import { SQL } from "bun";

const { db } = config;

const sql = new SQL({
  url: `postgresql://${db.user}:${db.password}@${db.host}:5432/${db.database}`,
  max: db.maxConnections,
  idleTimeout: 60,
  connectionTimeout: 30,
  maxLifetime: 300
});

export default sql;
