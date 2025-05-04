import { readFileSync } from "node:fs";
import { load } from "js-yaml";

const config = load(readFileSync("config.yaml", "utf8"));

export default config;
