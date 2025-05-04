FROM node:15.10.0 AS builder

WORKDIR /app

COPY package*.json ./

# RUN npm ci --only=production
RUN npm install

COPY . .

RUN npm run build

FROM node:15.10.0-alpine

WORKDIR /app

COPY --from=builder /app ./

USER node

CMD ["npm", "run", "start:prod"]
