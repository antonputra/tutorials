# Docker Networking Tutorial (Bridge - None - Host - IPvlan - Macvlan - Overlay)

You can find tutorial [here](https://youtu.be/fBRgw5dyBd4).

## Commands from the Tutorial


### Bridge

```bash
docker network ls
docker network inspect bridge
docker run -d --name myapp -p 8081:8080 aputra/myapp-188:v3
docker ps
docker inspect myapp
curl localhost:8081/api/info

docker run -d --name myapp-v2 -p 8082:8080 aputra/myapp-188:v3
docker ps

curl localhost:8081/api/info
curl localhost:8082/api/info
docker exec -it myapp sh

curl 172.17.0.2:8080/api/info
curl 172.17.0.3:8080/api/info

curl myapp-v2:8080/api/info

docker rm -f myapp myapp-v2

docker network create my-bridge-net --subnet 10.0.0.0/19 --gateway 10.0.0.1
docker network ls
docker network inspect my-bridge-net

docker run -d --name myapp -p 8081:8080 --network my-bridge-net aputra/myapp-188:v3
docker run -d --name myapp-v2 -p 8082:8080 --network my-bridge-net aputra/myapp-188:v3
curl localhost:8081/api/info
curl localhost:8082/api/info

docker exec -it myapp sh
curl myapp-v2:8080/api/info

docker rm -f myapp myapp-v2
docker network rm my-bridge-net

docker compose -f 1-compose.yaml up -d
```

### Host

```bash
docker run -d --name myapp --network host aputra/myapp-188:v3
docker ps

curl 192.168.50.55:8080/api/info

docker rm -f myapp
```

### None

```bash
docker run -d --name myapp --network none aputra/myapp-188:v3
docker exec myapp ip addr

docker run -d --name myapp -p 8081:8080 --network none aputra/myapp-188:v3
docker run -d --name myapp -p 8081:8080 aputra/myapp-188:v3
curl localhost:8081/api/info
```

## IPvlan

```bash
ip addr

docker network create -d ipvlan \
    --subnet=192.168.50.0/24 \
    --gateway=192.168.50.1 \
    -o ipvlan_mode=l2 \
    -o parent=ens33 my-ipvlan-net

docker network ls
docker run -d --name myapp --network my-ipvlan-net aputra/myapp-188:v3
docker inspect myapp

curl 192.168.50.2:8080/api/info
```

### Macvlan

```bash
docker network create -d macvlan \
  --subnet=192.168.50.0/24 \
  --gateway=192.168.50.1 \
  -o parent=ens33 my-macvlan-net

docker network ls

docker run -d --name myapp --network my-macvlan-net aputra/myapp-188:v3
docker inspect myapp
docker exec -it myapp sh
```

### Overlay

```bash
(host 1) ip addr
(host 1) sudo ethtool -K ens33 tx-checksum-ip-generic off

(host 2) ip addr
(host 2) sudo ethtool -K ens33 tx-checksum-ip-generic off

(host 1) docker swarm init
(host 2) docker swarm join ...
(host 1) docker network create -d overlay --attachable my-overlay-net
(host 1) docker network ls

(host 1) docker run -d --name myapp --network my-overlay-net aputra/myapp-188:v3
(host 2) docker network ls
(host 2) docker run -dit --name myapp-v2 --network my-overlay-net aputra/myapp-188:v3
(host 2) docker network ls
(host 2) docker exec -it myapp-v2 sh

curl myapp:8080/api/info
```
