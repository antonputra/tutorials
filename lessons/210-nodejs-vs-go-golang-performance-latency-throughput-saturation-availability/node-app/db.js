import postgres from "postgres";
import config from "./config.js";

// Creates a connection pool to connect to Postgres.
const sql = postgres({
  host: config.db.host,
  database: config.db.database,
  username: config.db.user,
  password: config.db.password,
  max: config.db.maxConnections,
});

export default sql;
