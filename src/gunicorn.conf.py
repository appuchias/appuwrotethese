# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from appuwrotethese.extras import ShellCodes
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
    preload_app = False
    # bind = "0.0.0.0:8000"
    # certfile = None
    # keyfile = None
    # pidfile = None


# Startup
def when_ready(_):
    print(ShellCodes.FG_GREEN + "Ready!\n" + ShellCodes.RESET)
