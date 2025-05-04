FROM node:22.9.0 AS build

COPY . /app

WORKDIR /app

RUN npm ci --omit=dev

FROM gcr.io/distroless/nodejs22-debian12

COPY --from=build /app /app

WORKDIR /app

CMD ["app.js"]