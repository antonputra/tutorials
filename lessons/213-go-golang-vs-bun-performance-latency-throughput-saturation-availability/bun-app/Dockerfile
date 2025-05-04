FROM oven/bun:1.1.29 AS build

WORKDIR /app

COPY . .

RUN bun install --frozen-lockfile --production

RUN bun run build

FROM oven/bun:1.1.29-distroless

COPY --from=build /app/bun-app /bun-app

ENTRYPOINT [ "/bun-app"]
