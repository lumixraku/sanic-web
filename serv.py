from sanic import Sanic
from sanic.response import empty

import controllers
from common.route_utility import autodiscover
from config import serv
from config.load_env import load_env

# 加载配置文件
load_env()

app = Sanic("sanic-web")
autodiscover(
    app,
    controllers,
    recursive=True,
)

app.route("/")(lambda _: empty())


if __name__ == "__main__":
    app.run(host=serv.host, port=serv.port, workers=serv.workers)
