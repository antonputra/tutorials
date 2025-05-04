all: build push restart

build:
	docker build -t aputrabay/express:latest -f express/Dockerfile express

push:
	docker push aputrabay/express:latest

restart:
	kubectl rollout restart deployment express

run:
	node express/server.js

run-docker:
	docker run -p 8080:8080 aputrabay/express:latest
