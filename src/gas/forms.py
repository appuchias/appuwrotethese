from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class SearchStations(forms.Form):
    """
    Form for searching stations
    """

    query = forms.CharField(
        label=_("Search query"),
        required=True,
        help_text=_("Specific element to look for (e.g. Coruña, 15001, etc.)"),
    )

    type = forms.ChoiceField(
        label=_("Search by"),
        choices=[
            ("locality", _("Locality")),
            ("province", _("Province")),
            ("postal_code", _("Postal code (Inaccurate)")),
        ],
        required=True,
        help_text=_("What the search query is"),
    )

    fuel = forms.ChoiceField(
        label=_("Fuel"),
        choices=[
            ("GOA", "Gasóleo A (Diesel)"),
            ("G95E5", "Gasolina 95"),
            ("G98E5", "Gasolina 98"),
            ("GLP", "GLP"),
        ],
        required=True,
        help_text=_("Fuel you're interested in (Results will be filtered by this)"),
    )

    query_date = forms.DateField(
        label=_("Date"),
        help_text=_("Date of the query"),
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
                    Div("query", css_class="col-md-6"),
                    Div("type", css_class="col-md-6"),
                    css_class="row",
                ),
                Div(
                    Div("fuel", css_class="col-md-6"),
                    Div("query_date", css_class="col-md-6"),
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
