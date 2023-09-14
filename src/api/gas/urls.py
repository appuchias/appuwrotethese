# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path
from api.gas import views

urlpatterns = [
    path("", views.home, name="home"),
    path("prices/", views.get_prices, name="get_prices"),
    path("prices/search/", views.search_prices, name="search_prices"),
    # path("stations/", views.get_stations, name="get_stations"),
    # path("stations/search/", views.search_stations, name="search_stations"),
]
