from django.urls import path
from accounts import views

urlpatterns = [
    path("", views.account),
    path("login/", views.acct_login),
    path("register/", views.acct_register),
    path("chpwd/", views.acct_change_pwd),
    # path("upgrade/", views.upgrade),
    path("respwd/", views.acct_reset_pwd),
    path("logout/", views.acct_logout),
]
