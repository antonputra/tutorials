import { readFileSync } from "fs";
import { load } from "js-yaml";
import type { Config } from "./types.ts";

const config: Config = load(readFileSync("config.yaml", "utf8")) as Config;

export default config;
