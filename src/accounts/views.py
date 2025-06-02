# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

import secrets, string

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

# Get django installed apps
from django.conf import settings

from accounts import forms

PASSWORD_CHARS = string.ascii_letters + string.digits + string.punctuation
PASSWORD_LENGTH = 16
PASSWORD_RESET_EMAIL = _(
    """Hello, {}

This is the response to your password reset request.
If you did not request a password reset, you can ignore this email.

Your new password is: {}

I would recommend using a password manager to have passwords just like that one created and automatically saved for all services without having to remember them.
A great option is Bitwarden (not sponsored).

Best regards,
- Appu
"""
)


@login_required
def account(request: HttpRequest):
    """Show account page"""

    show_gas = "gas" in settings.INSTALLED_APPS and False  # Disabled for now ---
    show_mastermind = "mastermind" in settings.INSTALLED_APPS

    stations = list()
    games = list()

    if show_gas:
        # from gas.models import Station
        ...

    if show_mastermind:
        from mastermind.models import Game

        games = list(Game.objects.filter(user=request.user).order_by("created"))

    return render(
        request,
        "accounts/account.html",
        {
            "user": request.user,
            "stations": stations,
            "gas": show_gas,
            "games": games,
            "mastermind": show_mastermind,
        },
    )


def profile(request: HttpRequest):
    """Show profile page"""

    return redirect("/accounts")


def acct_login(request: HttpRequest):
    """Login a user"""

    if request.user.is_authenticated:
        return redirect("/accounts")

    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"], "Method not allowed")

    if request.method == "GET":
        return render(request, "accounts/login.html", {"form": forms.AWTLoginForm})

    # POST
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, _("You are now logged in"))
    else:  # Wrong username or password
        messages.error(request, _("Wrong username or password"))

    return redirect("/accounts")


def acct_register(request: HttpRequest):
    """Register a new user"""

    if request.user.is_authenticated:
        return redirect("/accounts")

    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"], "Method not allowed")

    if request.method == "GET":
        return render(
            request,
            "accounts/register.html",
            {"form": forms.AWTUserCreationForm},
        )

    # POST
    form = forms.AWTUserCreationForm(request.POST)
    if not form.is_valid():
        for msg in form.error_messages.values():
            messages.error(request, msg)
        return redirect("/accounts/register")

    data = form.cleaned_data
    user = User.objects.create_user(
        username=data.get("username"),
        email=data.get("email"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        password=data.get("password1"),
    )
    user.save()
    messages.success(request, _("You are now registered"))

    return redirect("/accounts")


@login_required
def acct_change_pwd(request: HttpRequest):
    """Change password"""

    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"], "Method not allowed")

    if request.method == "GET":
        return render(
            request,
            "accounts/chpwd.html",
            {"chpwdform": forms.AWTPasswordChangeForm(user=request.user)},
        )

    # POST
    form = forms.AWTPasswordChangeForm(request.user, request.POST)
    if not form.is_valid():
        for msg in form.errors.values():
            messages.error(request, msg)
        return redirect("/accounts")

    data = form.cleaned_data
    user = authenticate(
        request, username=request.user.username, password=data.get("old_password")  # type: ignore
    )
    if user is not None:
        user = form.save()
        update_session_auth_hash(request, user)  # Important!
        messages.success(request, _("Your password was successfully updated!"))
    else:
        messages.error(request, _("Old password is not correct"))

    return redirect("/accounts")


def acct_reset_pwd(request: HttpRequest):
    """Reset password and send it to the user's email"""

    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"], "Method not allowed")

    if request.method == "GET":
        return render(
            request,
            "accounts/respwd.html",
            {"form": forms.AWTPasswordResetForm()},
        )

    # POST
    form = forms.AWTPasswordResetForm(request.POST)
    if not form.is_valid():
        for msg in form.errors.values():
            messages.error(request, msg)
        return redirect("/accounts")

    data = form.cleaned_data

    try:
        user = User.objects.get(email=data.get("email"))
    except User.DoesNotExist:
        messages.error(request, _("Email is not registered"))
        return redirect("/accounts")

    new_pwd = "".join(secrets.choice(PASSWORD_CHARS) for _ in range(PASSWORD_LENGTH))
    user.set_password(new_pwd)
    user.save()

    # Send email with new password through django
    user.email_user(
        _("[appu.ltd] Password reset email"),
        PASSWORD_RESET_EMAIL.format(user.username, new_pwd),
        "noreply@appu.ltd",
    )

    messages.success(
        request,
        _(
            "Your password was successfully reset. Please check your email with your new temporary password."
        ),
    )

    return redirect("/accounts")


@login_required
def acct_logout(request: HttpRequest):
    """Logout a user"""

    logout(request)
    return redirect("/accounts")


def why(request: HttpRequest):
    """Why page"""

    return render(request, "accounts/why.html")
