FROM node:15.8.0

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

USER node

CMD [ "node", "server.js" ]
