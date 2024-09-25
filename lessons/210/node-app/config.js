import { readFileSync } from "fs";
import { load } from "js-yaml";

export const config = load(readFileSync("config.yaml", "utf8"));
