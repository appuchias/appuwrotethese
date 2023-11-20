# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class MastermindGuess(forms.Form):
    game_id = forms.IntegerField(required=True)
    guess = forms.IntegerField(
        required=True,
        label=_("Guess"),
        min_value=0,
        max_value=9999,
        help_text=_("A 4-digit number."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(
                Div("game_id", css_class="invisible d-none"),
                "guess",
                Submit("submit", _("Guess"), css_class="btn btn-outline-dark"),
                css_class="card-body",
            ),
        )
