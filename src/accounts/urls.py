# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.urls import path
from accounts import views

urlpatterns = [
    path("", views.account),
    path("profile/", views.profile),
    path("login/", views.acct_login),
    path("register/", views.acct_register),
    path("chpwd/", views.acct_change_pwd),
    path("respwd/", views.acct_reset_pwd),
    path("logout/", views.acct_logout),
    path("why/", views.why),
]
