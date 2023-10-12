# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class SearchPrices(forms.Form):
    """Form for searching stations"""

    term = forms.CharField(
        label=_("Search term"),
        required=True,
        help_text=_("Specific term to look for (e.g. Coruña, 15001, etc.)"),
    )

    fuel_abbr = forms.ChoiceField(
        label=_("Fuel"),
        choices=[
            ("GOA", "Gasóleo A (Diésel)"),
            ("G95E5", "Gasolina 95"),
            ("G98E5", "Gasolina 98"),
            ("GLP", "GLP"),
        ],
        required=True,
        help_text=_("Fuel to use for sorting"),
    )

    q_date = forms.DateField(
        label=_("Date"),
        help_text=_("Prices date"),
        required=True,
        widget=forms.widgets.DateInput(
            attrs={
                "type": "date",
                "min": date(2007, 1, 1),
                "max": date.today(),
                "value": date.today(),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div("term", css_class="col-md-7"),
                Div("fuel_abbr", css_class="col"),
                Div("q_date", css_class="col"),
                css_class="row",
            ),
            Div(
                Submit(
                    "submit",
                    _("Search"),
                    css_class="btn btn-outline-dark",
                ),
                css_class="d-flex justify-content-end",
            ),
        )


class GetPrices(forms.Form):
    """Form for getting prices, knowing specific IDs"""

    locality_id = forms.IntegerField(
        label=_("Locality ID"),
        required=False,
        help_text=_("Locality ID"),
    )

    province_id = forms.IntegerField(
        label=_("Province ID"),
        required=False,
        help_text=_("Province ID"),
    )

    postal_code = forms.IntegerField(
        label=_("Postal code"),
        required=False,
        help_text=_("Postal code"),
    )

    fuel_abbr = forms.ChoiceField(
        label=_("Fuel"),
        choices=[
            ("GOA", "Gasóleo A (Diésel)"),
            ("G95E5", "Gasolina 95"),
            ("G98E5", "Gasolina 98"),
            ("GLP", "GLP"),
        ],
        required=True,
        help_text=_("Fuel to use for sorting"),
    )

    q_date = forms.DateField(
        label=_("Date"),
        help_text=_("Prices date"),
        required=True,
        widget=forms.widgets.DateInput(
            attrs={
                "type": "date",
                "min": date(2007, 1, 1),
                "max": date.today(),
                "value": date.today(),
            }
        ),
    )
