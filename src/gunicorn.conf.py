from appuwrotethese.extras import BashColors
from appuwrotethese.settings import DEBUG

wsgi_app = "appuwrotethese.wsgi:application"

# Production settings
workers = 2
bind = "0.0.0.0:8443"

# SSL
certfile = "./ssl/cert.pem"
keyfile = "./ssl/key.pem"

pidfile = "/tmp/gunicorn.pid"
# bind = "unix:/tmp/gunicorn.sock"

# Logging
access_log_format = '%(t)s %({cf-connecting-ip}i)s[%({cf-ipcountry}i)s]  "%(f)s" "%(r)s" -> %(s)s %(b)s "%(a)s"'
accesslog = "./log/access.log"
errorlog = "./log/gunicorn.log"
loglevel = "info"

# Connections
backlog = 256
worker_connections = 200

# Local development overrides
if DEBUG:
    reload = True
    workers = 1
    bind = "0.0.0.0:8000"
    preload_app = False
    certfile = None
    keyfile = None
    pidfile = None


# Startup
def when_ready(_):
    print(BashColors.FG_GREEN + "\nReady!\n" + BashColors.RESET)
