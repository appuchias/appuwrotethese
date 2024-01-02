# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.contrib import admin
from django.urls import path, include
from appuwrotethese import views

handler404 = "appuwrotethese.views.handler404"
handler500 = "appuwrotethese.views.handler500"

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("gas/", include("gas.urls")),
    path("accounts/", include("accounts.urls")),
    path("mastermind/", include("mastermind.urls")),
    path("i18n/", include("django.conf.urls.i18n"), name="i18n"),
    path("robots.txt", views.redirect_static, kwargs={"resource": "robots.txt"}),
    path("favicon.ico", views.redirect_static, kwargs={"resource": "favicon.ico"}),
    path("sitemap.xml", views.redirect_static, kwargs={"resource": "sitemap.xml"}),
]

urlpatterns += [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("legal/", views.legal, name="legal"),
    path("text/", views.text, name="text"),
    path("build/", views.build, name="build"),
    path("projects/", views.projects, name="projects"),
    path("teapot/", views.teapot, name="teapot"),
]
