 all: build push

build:
	docker build -t aputra/express-073:latest -f 0-express/Dockerfile 0-express

push:
	docker push aputra/express-073:latest

restart:
	kubectl rollout restart deployment express

run:
	node 0-express/server.js

run-docker:
	docker run -p 8080:8080 aputra/express-073:latest

prom:
	kubectl port-forward svc/prometheus-operated 9090 -n monitoring