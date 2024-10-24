FROM node:22.10

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

USER node

CMD [ "node", "server.js" ]
