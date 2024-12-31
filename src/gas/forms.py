# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from datetime import date, timedelta
from typing import Any, Mapping

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, HTML
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

FUEL_CHOICES = [
    ("price_goa", "Gasóleo A"),
    ("price_gob", "Gasóleo B"),
    ("price_g95e5", "Gasolina 95 E5"),
    # ("price_g95e5_premium", "Gasolina 95 E5 Premium"),
    # ("price_g95e10", "Gasolina 95 E10"),
    ("price_g98e5", "Gasolina 98 E5"),
    # ("price_g98e10", "Gasolina 98 E10"),
    ("price_glp", "GLP"),
    # ("price_gnc", "GNC"),
    # ("price_h2", "Hidrógeno"),
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
            (2, "2 km"),
            (3, "3 km"),
            (4, "4 km"),
            (5, "5 km"),
            (6, "6 km"),
            (10, "10 km"),
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
                HTML(
                    """
                    <div class="col" style="flex: 0.5">
                        <a class="btn btn-outline-dark" style="margin: 2rem 1rem" href="#" onClick="setCoords();">
                            <i data-lucide="locate-fixed"></i>
                        </a>
                    </div>
                    """
                ),
                Div("latitude", css_class="col"),
                Div("longitude", css_class="col"),
                Div("radius", css_class="col"),
                Div("fuel_abbr", css_class="col"),
                Div("q_date", css_class="col"),
                css_class="container-fluid row",
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


class DateRangeForm(forms.Form):
    """Form for selecting a date range"""

    start_date = forms.DateField(
        label=_("Start date"),
        help_text=_("Start date"),
        required=True,
        widget=forms.widgets.DateInput(
            attrs={
                "type": "date",
                "min": date(2007, 1, 1),
                "max": date.today(),
                "value": date.today() - timedelta(days=30),
            }
        ),
    )

    end_date = forms.DateField(
        label=_("End date"),
        help_text=_("End date"),
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

        # Set crispy form layout
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div("start_date"),
                HTML("<span>&nbsp;-&nbsp;</span>"),
                Div("end_date"),
                css_class="d-flex justify-content-center",
            ),
        )
