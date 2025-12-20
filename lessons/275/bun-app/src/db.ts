import config from "./config.ts";
import { SQL } from "bun";
import type { Config } from "./types.ts";

const sql = new SQL({
  url: `postgres://${(config as Config).db.user}:${(config as Config).db.password}@${(config as Config).db.host}:5432/${(config as Config).db.database}`,
  max: (config as Config).db.maxConnections,
});

export default sql;
