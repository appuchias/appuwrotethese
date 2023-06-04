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

    q_type = forms.ChoiceField(
        label=_("Search by"),
        choices=[
            ("locality", _("Locality")),
            ("province", _("Province")),
            ("postal_code", _("Postal code")),
        ],
        required=True,
        help_text=_("Type of query"),
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

    # star = forms.BooleanField(
    #     label=gettext_lazy("Star query"),
    #     required=False,
    #     help_text=gettext_lazy(
    #         "(Save this query. Requires your account to be upgraded)"
    #     ),
    # )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Div("term", css_class="col-md-6"),
                    Div("q_type", css_class="col-md-6"),
                    css_class="row",
                ),
                Div(
                    Div("fuel_abbr", css_class="col-md-6"),
                    Div("q_date", css_class="col-md-6"),
                    css_class="row",
                ),
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
