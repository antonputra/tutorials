# Docker Compose Tutorial for Beginners (Networks - Volumes - Secrets - Postgres - Letsencrypt)

You can find tutorial [here](https://youtu.be/YMBT1NguJJw).

## Commands

```
python3 -m venv .venv
source .venv/bin/activate
pip install Flask
pip freeze > requirements.txt
flask --app app run
curl 127.0.0.1:5000/about
export APP_VERSION=0.1.0
env | grep APP_VERSION
pip install gunicorn
docker build -t aputra/flask:0.1.0 .
docker run -p 7070:8080 aputra/flask:0.1.0
curl localhost:7070/about
docker run -p 7070:8080 -e APP_VERSION=0.1.0 aputra/flask:0.1.0
deactivate
docker compose up
docker build -t aputra/flask:latest .
docker compose up --build
APP_TOKEN=secret123 docker compose up
curl -X POST localhost:7070/volumes
curl -X GET localhost:7070/volumes

docker ps

docker exec -it 199-postgres-1 psql -h localhost -p 5432 -U myuser -d mydb

CREATE TABLE item (
  item_id serial PRIMARY KEY,
  priority varchar(256),
  task varchar(256)
);


CREATE USER myapp WITH PASSWORD 'devops123';
GRANT ALL PRIVILEGES ON DATABASE mydb to myapp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO myapp;

pip install "psycopg[binary,pool]"

curl -H "Content-Type: application/json" -d '{"priority":"high","task":"doctor appointment"}' localhost:7070/items

curl -H "Content-Type: application/json" -d '{"priority":"low","task":"buy dinner"}' localhost:7070/items

SELECT * FROM item;

curl localhost:7070/items
```