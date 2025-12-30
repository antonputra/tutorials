import { load } from "js-yaml";
import type { Config } from "./types.ts";

const config: Config = load(await Bun.file("config.yaml").text()) as Config;

export default config;
