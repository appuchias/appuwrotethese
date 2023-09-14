# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from gas.models import Station


class SavedStation(models.Model):
    """Model for storing saved stations"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user.username}: {self.station.id_eess}"

    class Meta:
        verbose_name = _("Saved Station")
        verbose_name_plural = _("Saved Stations")

        ordering = ["user"]


class SavedQuery(models.Model):
    """Model for storing saved queries"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    term = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9_]*$",
                message=_("Only alphanumeric characters and underscores are allowed."),
            )
        ],
    )

    q_type = models.CharField(
        max_length=100,
        choices=[
            ("locality", _("Locality")),
            ("province", _("Province")),
            ("postal_code", _("Postal code")),
        ],
    )

    fuel_abbr = models.CharField(
        max_length=100,
        choices=[
            ("GOA", "Diesel"),
            ("G95E5", "Gasolina 95"),
            ("G98E5", "Gasolina 98"),
            ("GLP", "Gases Licuados del Petróleo"),
        ],
    )

    def __str__(self):
        return f"{self.user.username}: {self.term} ({self.fuel_abbr})"

    class Meta:
        verbose_name = _("Saved Query")
        verbose_name_plural = _("Saved Queries")

        ordering = ["user"]
