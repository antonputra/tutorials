FROM oven/bun:1.3.5 AS build

WORKDIR /app

COPY package.json bun.lock ./

RUN bun install --frozen-lockfile --production

COPY ./src ./src

RUN bun run build

FROM oven/bun:1.3.5-slim

COPY --from=build /app/bun-app /bun-app

ENTRYPOINT [ "/bun-app"]
