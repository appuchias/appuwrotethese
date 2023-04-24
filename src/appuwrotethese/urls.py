from django.contrib import admin
from django.urls import path, include
from appuwrotethese import views

handler404 = "appuwrotethese.views.handler404"
handler500 = "appuwrotethese.views.handler500"

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("gas/", include("gas.urls")),
    # path("account/", include("accounts.urls")),
    path("i18n/", include("django.conf.urls.i18n"), name="i18n"),
]

urlpatterns += [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("thanks/", views.thanks, name="thanks"),
    path("text/", views.text, name="text"),
    path("build/", views.build, name="build"),
    path("projects/", views.projects, name="projects"),
]
