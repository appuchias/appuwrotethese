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

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


# User creation form for the web
class AWTUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        help_text=_(
            "Required. Your email will be used for password resetting and account activation."
        ),
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Div("username", css_class="col-md-6"),
                    Div("email", css_class="col-md-6"),
                    css_class="row",
                ),
                Div(
                    Div("first_name", css_class="col-md-6"),
                    Div("last_name", css_class="col-md-6"),
                    css_class="row",
                ),
                "password1",
                "password2",
            ),
            Div(
                Submit(
                    "submit",
                    _("Register"),
                    css_class="btn btn-outline-dark",
                ),
                css_class="d-flex justify-content-end",
            ),
        )


class AWTLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div("username", css_class="row"),
                Div("password", css_class="row"),
                css_class="col",
            ),
            Div(
                Div(
                    Submit(
                        "submit",
                        _("Login"),
                        css_class="btn btn-outline-dark",
                    ),
                ),
                css_class="d-flex justify-content-end",
            ),
        )


class AWTPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = (
            "old_password",
            "new_password1",
            "new_password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("old_password", css_class="row"),
            Div(
                Div("new_password1", css_class="col"),
                Div("new_password2", css_class="col"),
                css_class="row",
            ),
            Div(
                Submit(
                    "submit",
                    _("Change password"),
                    css_class="btn btn-outline-dark",
                ),
                css_class="d-flex justify-content-end",
            ),
        )


class AWTPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        help_text=_(
            "Required. You will receive an email with your temporary password."
        ),
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("email", css_class="row"),
            Div(
                Submit(
                    "submit",
                    _("Reset password"),
                    css_class="btn btn-outline-dark",
                ),
                css_class="d-flex justify-content-end",
            ),
        )


class AWTUpgradeForm(forms.Form):
    upgrade_uuid = forms.CharField(
        label=_("Upgrade UUID"),
        help_text=_(
            "You will receive an email regarding your purchase from sellix with your upgrade UUID."
        ),
        max_length=24,
        required=True,
        validators=[
            RegexValidator("^[a-f0-9]{6}-[a-f0-9]{10}-[a-f0-9]{6}$", "Invalid UUID")
        ],
    )

    class Meta:
        model = User
        fields = ("upgrade_uuid",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("upgrade_uuid", css_class="row"),
            Div(
                Submit(
                    "submit",
                    _("Upgrade"),
                    css_class="btn btn-outline-dark",
                ),
                css_class="d-flex justify-content-end",
            ),
        )
