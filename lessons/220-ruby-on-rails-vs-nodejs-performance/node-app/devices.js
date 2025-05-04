import sql from "./db.js";

// Inserts a Device into the Postgres database.
async function save({ uuid, mac, firmware, created_at, updated_at }) {
  return sql`INSERT INTO "node_device" ("uuid", "mac", "firmware", "created_at", "updated_at") VALUES (${uuid}, ${mac}, ${firmware}, ${created_at}, ${updated_at}) RETURNING "id";`;
}

export default save;
