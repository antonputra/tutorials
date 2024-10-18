FROM denoland/deno:2.0.0

WORKDIR /app

USER deno

COPY . .

# The deno cache command has been merged into the deno install command under the --entrypoint option.
RUN deno install --entrypoint app.js

CMD ["run", "--allow-net", "--allow-read", "app.js"]
