import secrets
import string
from os import getenv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.mail import send_mail
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from sellix import Sellix

from appuwrotethese import extras
from accounts import forms, models

load_dotenv()

client = Sellix(api_key=getenv("SELLIX_API_KEY", ""))


def _validate_order(order_id: str) -> bool:
    order = client.get_order(order_id)
    return order["status"].lower() == "completed"


def account(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("/account/login")

    user = extras.get_user(request)
    # if user.is_authenticated and not user.is_upgraded:
    #     messages.warning(
    #         request,
    #         _(
    #             "Your account is not upgraded. You can log in but you won't have access to all features."
    #         ),
    #     )
    return render(request, "accounts/account.html", {"awtuser": user})


def acct_login(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("/account")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _("You are now logged in"))
        else:  # Wrong username or password
            messages.error(request, _("Wrong username or password"))
    else:  # GET request
        return render(request, "accounts/login.html", {"loginform": forms.AWTLoginForm})
    return redirect("/account")


def acct_register(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("/account")

    if request.method == "POST":
        form = forms.AWTUserCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = models.AWTUser.objects.create_user(
                username=data["username"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                password=data["password1"],
            )
            user.save()
            messages.success(request, _("You are now registered"))
        else:  # Form is not valid
            for msg in form.error_messages.values():
                messages.error(request, msg)
    else:  # GET request
        return render(
            request,
            "accounts/register.html",
            {"registrationform": forms.AWTUserCreationForm},
        )
    return redirect("/account")


def acct_change_pwd(request: HttpRequest):
    if request.method == "POST":
        form = forms.AWTPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request,
                username=request.user.username,
                password=data["old_password"],
            )
            if user is not None:
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, _("Your password was successfully updated!"))
            else:
                messages.error(request, _("Old password is not correct"))
        else:
            for msg in form.error_messages.values():
                messages.error(request, msg)
        return redirect("/account")

    return render(
        request,
        "accounts/chpwd.html",
        {
            "chpwdform": forms.AWTPasswordChangeForm(user=request.user),
        },
    )


def acct_reset_pwd(request: HttpRequest):
    if request.method == "POST":
        form = forms.AWTPasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if user := models.AWTUser.objects.get(email=data["email"]):
                new_pwd = "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for _ in range(20)
                )
                user.set_password(new_pwd)
                user.save()
                email_content = f"""
Hi, @{user.username}

This email is the response to your password reset request.
If you did not request a password reset, please ignore this email.

Your new password is: {new_pwd}

I would recommend using a password manager to have passwords just like that one created and automatically saved for all services without having to remember them.
A great option is Bitwarden (not sponsored)

Best regards,
- Appu
"""
                # Send email with new password through django
                send_mail(
                    _("[appu.ltd] Password reset email"),
                    email_content,
                    "accounts@appu.ltd",
                    [user.email],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    _(
                        "Your password was successfully reset.\
                        Please check your email with your new temporary password."
                    ),
                )
            else:
                messages.error(request, _("Email is not registered"))
        else:
            for msg in form.error_messages.values():
                messages.error(request, msg)

        return redirect("/account")

    return render(
        request,
        "accounts/respwd.html",
        {
            "respwdform": forms.AWTPasswordResetForm(),
        },
    )


def acct_logout(request: HttpRequest):
    logout(request)
    return redirect("/account")


# def upgrade(request: HttpRequest):
#     if not request.user.is_authenticated:  # I need the account to upgrade
#         messages.error(
#             request,
#             _("You are not logged in. Please log in before upgrading your account."),
#         )
#         return redirect("/account")

#     user = extras.get_user(request)

#     if user.is_upgraded:  # There's no point in upgrading twice
#         messages.error(request, _("You already have an upgraded account."))
#         return redirect("/account")

#     if request.method == "POST":
#         form = forms.AWTUpgradeForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             if not _validate_order(data["upgrade_uuid"]):
#                 messages.error(
#                     request,
#                     _(
#                         "Upgrade UUID does not match any order or your order has not been completed yet."
#                     ),
#                 )
#                 return redirect("/account/upgrade")
#             if models.AWTUser.objects.filter(
#                 upgrade_uuid=data["upgrade_uuid"]
#             ).exists():
#                 messages.error(
#                     request,
#                     _(
#                         "This upgrade UUID has already been used. Please contact me if you think this is a mistake."
#                     ),
#                 )
#                 return redirect("/account/upgrade")
#             if user is not None:
#                 user.is_upgraded = True
#                 user.upgrade_uuid = data["upgrade_uuid"]
#                 user.save()
#                 messages.success(request, _("Your account has been upgraded!"))
#             else:
#                 messages.error(request, _("Wrong password"))
#         else:
#             messages.error(request, "Error validating form.")
#         return redirect("/account")

#     return render(
#         request,
#         "accounts/upgrade.html",
#         {"upgradeform": forms.AWTUpgradeForm, "awtuser": user},
#     )
