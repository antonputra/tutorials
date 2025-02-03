FROM oven/bun:1.2.2 AS build

WORKDIR /app

COPY . .

RUN bun install --frozen-lockfile --production

RUN bun run build

FROM oven/bun:1.2.2-distroless

COPY --from=build /app/bun-app /bun-app

ENTRYPOINT [ "/bun-app"]