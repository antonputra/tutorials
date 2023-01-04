FROM node:18 AS build

WORKDIR /app

COPY service-a.js package*.json .

RUN npm ci --only=production

FROM gcr.io/distroless/nodejs18-debian11

COPY --from=build /app /app

WORKDIR /app

CMD ["service-a.js"]
