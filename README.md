# q2bot

See [Docs](https://v2.nonebot.dev/)

## 构建docker

```shell
nb docker build
docker compose logs -f
docker compose up -d
docker compose down

pip freeze > requirements.txt
pip install -r requirements.txt
win:  .\.venv\Scripts\activate  

uvloop==0.17.0;sys_platform != 'win32'
```

## 运行
```shell
nb run --reload
```

## psql

```shell
# 添加一个表字段
ALTER TABLE user_table
ADD COLUMN email varchar(255);

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

## 代码提交规范

type: commit 的类型
feat: 新特性
fix: 修改问题
refactor: 代码重构
docs: 文档修改
style: 代码格式修改, 注意不是 css 修改
test: 测试用例修改
chore: 其他修改, 比如构建流程, 依赖管理.
scope: commit 影响的范围, 比如: route, component, utils, build...
subject: commit 的概述, 建议符合 50/72 formatting
body: commit 具体修改内容, 可以分为多行, 建议符合 50/72 formatting
footer: 一些备注, 通常是 BREAKING CHANGE 或修复的 bug 的链接.

