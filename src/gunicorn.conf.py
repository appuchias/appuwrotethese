# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from appuwrotethese.extras import ShellCodes
from appuwrotethese.settings import DEBUG

wsgi_app = "appuwrotethese.wsgi:application"

# Connections
backlog = 128
worker_connections = 200

pidfile = "gunicorn.pid"


# PROD
if not DEBUG:
    # workers = 2
    bind = "0.0.0.0:8443"

    # SSL
    certfile = "./ssl/cert.pem"
    keyfile = "./ssl/key.pem"
else:
    # workers = 1
    bind = "0.0.0.0:8000"

    reload = True

# Logging
access_log_format = '%(t)s %({cf-connecting-ip}i)s[%({cf-ipcountry}i)s]  "%(f)s" "%(r)s" -> %(s)s %(b)s "%(a)s"'
accesslog = "./log/access.log"
errorlog = "./log/gunicorn.log"
loglevel = "info"


# Startup message
def when_ready(_):
    print(ShellCodes.FG_YELLOW + "Ready!\n" + ShellCodes.RESET)
