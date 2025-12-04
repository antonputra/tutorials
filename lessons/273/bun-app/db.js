import config from "./config.js";
import { SQL } from "bun";

const sql = new SQL({
  url: `postgres://${config.db.user}:${config.db.password}@${config.db.host}:5432/${config.db.database}`,
  max: config.db.maxConnections,
});

export default sql;
