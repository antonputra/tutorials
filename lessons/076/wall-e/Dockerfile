FROM public.ecr.aws/lambda/nodejs:14

COPY *.js package*.json  /var/task/

RUN npm ci --production

CMD [ "app.handler" ]
