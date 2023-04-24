from django.utils.translation import gettext_lazy
from django import forms
from crispy_forms.layout import Layout, Div, Submit
from crispy_forms.helper import FormHelper


class SearchStations(forms.Form):
    """
    Form for searching stations
    """

    query = forms.CharField(
        label=gettext_lazy("Search query"),
        required=True,
        help_text=gettext_lazy(
            "Specific element to look for (e.g. Coruña, 15001, etc.)"
        ),
    )

    type = forms.ChoiceField(
        label=gettext_lazy("Search by"),
        choices=[
            ("locality", gettext_lazy("Locality")),
            ("province", gettext_lazy("Province")),
            ("postal_code", gettext_lazy("Postal code (Inaccurate)")),
        ],
        required=True,
        help_text=gettext_lazy("What the search query is"),
    )

    fuel = forms.ChoiceField(
        label=gettext_lazy("Fuel"),
        choices=[
            ("GOA", "Gasóleo A (Diesel)"),
            ("G95E5", "Gasolina 95"),
            ("G98E5", "Gasolina 98"),
            ("GLP", "GLP"),
        ],
        required=True,
        help_text=gettext_lazy(
            "Fuel you're interested in (Results will be filtered by this)"
        ),
    )

    # star = forms.BooleanField(
    #     label=gettext_lazy("Star query"),
    #     required=False,
    #     help_text=gettext_lazy(
    #         "(Save this query. Requires your account to be upgraded)"
    #     ),
    # )

    show_all = forms.BooleanField(
        label=gettext_lazy("Show all"),
        required=False,
        help_text=gettext_lazy(
            "(Show all fuel types, not only the one you're looking for)"
        ),
        initial=True,
    )

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
                "fuel",
            ),
            Div(
                Div(
                    Div("show_all"),
                    # Div("star"),
                ),
                Submit(
                    "submit",
                    gettext_lazy("Search"),
                    css_class="btn btn-outline-dark",
                ),
                css_class="d-flex justify-content-between",
            ),
        )
