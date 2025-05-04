import Memcached from "memcached";
import config from "./config.js";

Memcached.config.poolSize = config.cache.poolSize;

const memcached = new Memcached(`${config.cache.host}:11211`);

export default memcached;
