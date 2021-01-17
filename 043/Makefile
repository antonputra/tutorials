APP=043
REPO=antonputra
VERSION=v0.1.5

.PHONY: build push
all: build push

build:
	docker build -t ${REPO}/${APP}:${VERSION} -f ./app/Dockerfile ./app

push:
	docker push ${REPO}/${APP}:${VERSION}

create-eks:
	eksctl create cluster -f eks.yaml

delete-eks:
	eksctl delete cluster -f eks.yaml
