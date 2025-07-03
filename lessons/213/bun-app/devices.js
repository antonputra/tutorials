import db from "./db.js";

// Inserts a Device into the MongoDB database.
const save = async (device) => db.collection("bun_devices").insertOne(device);

export default save;
