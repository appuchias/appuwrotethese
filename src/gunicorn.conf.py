# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import os

from appuwrotethese.extras import ShellCodes
from appuwrotethese.settings import DEBUG

wsgi_app = "appuwrotethese.wsgi:application"

# Connections
backlog = 128
worker_connections = 200

pidfile = "gunicorn.pid"


# PROD
if os.getenv("PROD", False) == "true" and not "virtualenvs" in os.getenv("PATH"):
    if (
        os.getenv("HTTPS", False) == "true"
        and os.path.exists("./ssl/cert.pem")
        and os.path.exists("./ssl/key.pem")
    ):
        bind = "0.0.0.0:443"
        certfile = "./ssl/cert.pem"
        keyfile = "./ssl/key.pem"
    else:
        bind = "0.0.0.0:80"
else:
    bind = "0.0.0.0:8000"


# Logging
access_log_format = '%(t)s %({cf-connecting-ip}i)s[%({cf-ipcountry}i)s]  "%(f)s" "%(r)s" -> %(s)s %(b)s "%(a)s"'
accesslog = "./log/access.log"
errorlog = "./log/gunicorn.log"
loglevel = "info"


# Startup message
def when_ready(_):
    print(ShellCodes.FG_YELLOW + "Ready!\n" + ShellCodes.RESET)
