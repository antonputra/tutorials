import { buildSync } from "esbuild"

buildSync({
  entryPoints: ["./app.js"],
  legalComments: "none",
  sourcemap: true,
  packages: "external",
  outdir: "dist",
  target: "node20",
  platform: "node",
  format: "esm",
  minify: true,
  bundle: true,
  // drop: ["console", "debugger"],
})
