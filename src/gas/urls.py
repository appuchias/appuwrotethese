# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path
from gas import views

urlpatterns = [
    path("", views.search),
    path("geo/", views.search, kwargs={"geo": True}),
    path("search/", views.result),
    path("search/geo/", views.result_geo),
    path("localities/", views.names, kwargs={"q_type": "locality"}),
    path("provinces/", views.names, kwargs={"q_type": "province"}),
    path("station/<int:id_eess>", views.station),
    # path("save/<int:id>", views.save),
]
