# 使用 python:3.10 作为基础镜像。这是一个官方的 Python 镜像，预装了 Python 3.10。
FROM python:3.10 as requirements_stage

# 创建一个名为 /wheel 的目录，并将其设置为后续命令的工作目录。如果该目录不存在，Docker 会自动创建它。
WORKDIR /wheel

# 使用 Python 的 pip 模块安装 pipx
RUN python -m pip install --user pipx

# 使用 COPY 命令将当前上下文（或构建上下文）中的 pyproject.toml 和 requirements.txt 文件复制到容器内的 /wheel 目录下
COPY ./pyproject.toml \
  ./requirements.txt \
  /wheel/


# 构建 requirements.txt 中列出的所有依赖的轮文件，并存储在 /wheel 目录中。禁用缓存以减小构建大小。
RUN python -m pip wheel --wheel-dir=/wheel --no-cache-dir --requirement ./requirements.txt

# 使用 pipx 在隔离环境中运行 nb-cli，生成或配置 /tmp/bot.py 文件。禁用缓存确保使用最新版本的 nb-cli。
RUN python -m pipx run --no-cache nb-cli generate -f /tmp/bot.py

# 设置基础镜像为 python:3.10-slim
FROM python:3.10-slim

# 设置工作目录为 /app
WORKDIR /app

# 设置环境变量 TZ 为 Asia/Shanghai 和 PYTHONPATH 为 /app
ENV TZ Asia/Shanghai
ENV PYTHONPATH=/app

# 复制 gunicorn 配置文件和启动脚本到容器根目录，并给启动脚本设置执行权限
COPY ./docker/gunicorn_conf.py ./docker/start.sh /
RUN chmod +x /start.sh

# 设置环境变量 APP_MODULE 为 _main:app 和 MAX_WORKERS 为 1
ENV APP_MODULE _main:app
ENV MAX_WORKERS 1

# 在这个阶段安装 Playwright 和 Chromium
RUN pip install playwright
RUN playwright install chromium --with-deps

# 从 requirements_stage 阶段复制 /tmp/bot.py 和 /wheel 目录到 /app
COPY --from=requirements_stage /tmp/bot.py /app
COPY ./docker/_main.py /app
COPY --from=requirements_stage /wheel /wheel

# 安装 gunicorn, uvicorn[standard], nonebot2 和 /wheel 目录中的所有依赖，然后删除 /wheel 目录
RUN pip install --no-cache-dir gunicorn uvicorn[standard] nonebot2 \
  && pip install --no-cache-dir --no-index --force-reinstall --find-links=/wheel -r /wheel/requirements.txt && rm -rf /wheel

# 复制当前目录下的所有文件到 /app/ ，外接挂载的文件会覆盖这些文件，所以不执行这一步
COPY . /app/

# 清理 apt 缓存，更新系统，安装 locales 包
RUN apt-get clean && apt-get update && apt-get install -y locales

# 生成 'zh_CN.UTF-8' locale
RUN sed -i -e 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

# 设置语言
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN:zh
ENV LC_ALL zh_CN.UTF-8

RUN locale -a

# 设置容器启动时执行的命令
CMD ["/start.sh"]