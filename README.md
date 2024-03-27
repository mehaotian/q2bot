# q2bot

See [Docs](https://v2.nonebot.dev/)

## 构建docker

```shell
nb docker build
docker compose logs -f
docker compose up -d
docker compose down
```

## 本地运行 env

```shell
ENVIRONMENT=dev
DRIVER=~fastapi+~httpx+~websockets
HOST=127.0.0.1
PORT=8080
SUPERUSERS=[1253567179,490272692]
db_url=postgres://postgres:1qaz!QAZ@localhost:5432/botdb

```
