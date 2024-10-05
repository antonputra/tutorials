import { MongoClient } from "mongodb";
import config from "./config.js";

const uri = `mongodb://${config.db.host}:27017`;
const client = new MongoClient(uri, { maxPoolSize: config.db.maxPoolSize });
const db = client.db(config.db.database);

export default db;
