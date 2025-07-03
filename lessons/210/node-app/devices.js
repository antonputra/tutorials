import sql from "./db.js";

// Inserts a Device into the Postgres database.
async function save({ uuid, mac, firmware }) {
  return sql`INSERT INTO "node_device" (id, mac, firmware) VALUES (${uuid}, ${mac}, ${firmware})`;
}

export default save;
