FROM denoland/deno:2.5.6

WORKDIR /app

USER deno

COPY . .

RUN deno install --entrypoint app.js

CMD ["run", "--allow-env", "--allow-net", "--allow-read", "--allow-sys", "app.js"]
