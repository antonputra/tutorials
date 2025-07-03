FROM node:23.7.0 AS build

COPY . /app

WORKDIR /app

RUN npm ci --omit=dev

FROM node:23.7.0-slim

COPY --from=build /app /app

WORKDIR /app

CMD ["app.js"]