
# 使用官方Python基础镜像
# base image
FROM python:3.10-slim-bookworm AS base

# 设置工作目录
WORKDIR /sanic-web

# 复制当前目录的内容到容器中的/app目录
COPY . /sanic-web

# 安装Poetry
ENV POETRY_VERSION=1.8.3

RUN pip install poetry==${POETRY_VERSION}

# 将 Poetry 安装路径添加到环境变量
ENV PATH="${PATH}:/root/.local/bin"

# 配置清华PyPI镜像
RUN poetry source add --priority=primary mirrors https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装依赖
RUN poetry lock --no-update

# 这里使用系统默认的python环境
RUN poetry env use system

# 安装依赖
RUN poetry install --no-root


# 暴露端口
EXPOSE 8088

# 运行命令 source命令激活相应的虚拟环境
CMD ["/bin/bash", "-c", "source $(poetry env info --path)/bin/activate && python3 serv.py"]
