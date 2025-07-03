FROM node:23.6.0-bookworm AS build

COPY . /app

WORKDIR /app

RUN npm ci --omit=dev

FROM node:23.6.0-bookworm-slim

COPY --from=build /app /app

WORKDIR /app

CMD ["app.js"]