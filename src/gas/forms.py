# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


FUEL_CHOICES = [
    ("GOA", "Gasóleo A"),
    ("GOB", "Gasóleo B"),
    ("G95E5", "Gasolina 95 E5"),
    # ("G95E5+", "Gasolina 95 E5 Premium"),
    # ("G95E10", "Gasolina 95 E10"),
    ("G98E5", "Gasolina 98 E5"),
    # ("G98E10", "Gasolina 98 E10"),
    ("GLP", "GLP"),
    # ("GNC", "GNC"),
    # ("H2", "Hidrógeno"),
]


class SearchPrices(forms.Form):
    """Form for searching stations"""

    term = forms.CharField(
        label=_("Search term"),
        required=True,
        help_text=_("Specific term to look for (e.g. Coruña, 15001, etc.)"),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    fuel_abbr = forms.ChoiceField(
        label=_("Fuel"),
        choices=FUEL_CHOICES,
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

        # Update q_date widget to set max and value to today
        self.fields["q_date"].widget.attrs.update(
            {"max": date.today(), "value": date.today()}
        )

        # Set crispy form layout
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div("term", css_class="col-md-7"),
                Div("fuel_abbr", css_class="col"),
                Div("q_date", css_class="col"),
                css_class="row",
            ),
            Div(
                Submit("submit", _("Search"), css_class="btn btn-outline-dark"),
                css_class="d-flex justify-content-end",
            ),
        )


class SearchPricesGeo(forms.Form):
    """Form for searching stations by coordinates

    This form is used to search for stations by coordinates and radius.
    """

    latitude = forms.FloatField(
        label=_("Latitude"),
        required=True,
        help_text=_("Latitude value"),
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )

    longitude = forms.FloatField(
        label=_("Longitude"),
        required=True,
        help_text=_("Longitude value"),
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    radius = forms.ChoiceField(
        label=_("Radius"),
        choices=[
            (1, "1 km"),
            (5, "5 km"),
            (10, "10 km"),
            (20, "20 km"),
            (50, "50 km"),
            (100, "100 km"),
        ],
        required=True,
        help_text=_("Max straight line distance"),
    )

    fuel_abbr = forms.ChoiceField(
        label=_("Fuel"),
        choices=FUEL_CHOICES,
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

        # Update q_date widget to set max and value to today
        self.fields["q_date"].widget.attrs.update(
            {"max": date.today(), "value": date.today()}
        )

        # Set crispy form layout
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div("latitude", css_class="col"),
                Div("longitude", css_class="col"),
                Div("radius", css_class="col"),
                Div("fuel_abbr", css_class="col"),
                Div("q_date", css_class="col"),
                css_class="row",
            ),
            Div(
                Submit("submit", _("Search"), css_class="btn btn-outline-dark"),
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
