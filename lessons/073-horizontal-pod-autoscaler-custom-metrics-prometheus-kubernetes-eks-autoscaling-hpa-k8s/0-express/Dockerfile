FROM amd64/node:16-alpine3.11

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm ci --only=production

COPY server.js .

CMD [ "node", "server.js" ]
