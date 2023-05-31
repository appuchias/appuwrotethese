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

from django.contrib import admin
from django.urls import path, include
from appuwrotethese import views

handler404 = "appuwrotethese.views.handler404"
handler500 = "appuwrotethese.views.handler500"

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("api/", include("api.urls")),
    path("gas/", include("gas.urls")),
    # path("account/", include("accounts.urls")),
    path("i18n/", include("django.conf.urls.i18n"), name="i18n"),
    path("robots.txt", views.redirect_static, kwargs={"resource": "robots.txt"}),
    path("favicon.ico", views.redirect_static, kwargs={"resource": "favicon.ico"}),
]

urlpatterns += [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("thanks/", views.thanks, name="thanks"),
    path("text/", views.text, name="text"),
    path("build/", views.build, name="build"),
    path("projects/", views.projects, name="projects"),
    path("teapot/", views.teapot, name="teapot"),
]
