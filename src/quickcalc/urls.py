# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path
from quickcalc import views

urlpatterns = [
    path("", views.quickcalc, name="quickcalc"),
]
