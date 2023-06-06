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

import secrets, string

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

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

    return render(request, "accounts/account.html", {"user": request.user})


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
        return redirect("/accounts")

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

    user = User.objects.get(email=data.get("email"))
    if not user:
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
