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

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Locality(models.Model):
    """
    Model for storing localities (Added for search optimization)
    """

    id_mun = models.IntegerField(
        verbose_name=_("Locality ID"),
        help_text=_("ID of the locality"),
        unique=True,
        primary_key=True,
    )

    name = models.CharField(
        verbose_name=_("Locality"),
        max_length=64,
    )

    class Meta:
        verbose_name = _("Locality")
        verbose_name_plural = _("Localities")

        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Province(models.Model):
    """
    Model for storing provinces (Added for search optimization)
    """

    id_prov = models.IntegerField(
        verbose_name=_("Province ID"),
        help_text=_("ID of the province"),
        unique=True,
        primary_key=True,
    )

    name = models.CharField(
        verbose_name=_("Province"),
        max_length=64,
    )

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")

        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Station(models.Model):
    id_eess = models.IntegerField(
        primary_key=True,
        verbose_name="ID_EESS",
        unique=True,
        auto_created=False,
    )

    company = models.CharField(verbose_name=_("Company"), max_length=128, blank=False)
    address = models.CharField(verbose_name=_("Address"), max_length=128, blank=False)
    schedule = models.CharField(verbose_name=_("Schedule"), max_length=64, blank=False)
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    postal_code = models.IntegerField(
        verbose_name=_("Postal code"),
        validators=[MaxValueValidator(99999)],
        default=00000,
    )
    latitude = models.CharField(
        verbose_name=_("Latitude"),
        max_length=10,
        blank=False,
        default="0",
    )
    longitude = models.CharField(
        verbose_name=_("Longitude"),
        max_length=10,
        blank=False,
        default="0",
    )

    class Meta:
        verbose_name = _("Gas station")
        verbose_name_plural = _("Gas stations")

        ordering = ["id_eess"]

    def __str__(self):
        return self.company + ", " + self.address


class StationPrice(models.Model):
    date = models.DateField(db_index=True, default=now)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    price_goa = models.DecimalField(
        verbose_name="Gasoleo A",
        max_digits=4,
        decimal_places=3,
        null=True,  # This will go wrong at some point
        default=None,
    )
    price_g95e5 = models.DecimalField(
        verbose_name="Gasolina 95",
        max_digits=4,
        decimal_places=3,
        null=True,
        default=None,
    )
    price_g98e5 = models.DecimalField(
        verbose_name="Gasolina 98",
        max_digits=4,
        decimal_places=3,
        null=True,
        default=None,
    )
    price_glp = models.DecimalField(
        verbose_name="GLP",
        max_digits=4,
        decimal_places=3,
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = _("Gas station price")
        verbose_name_plural = _("Gas station prices")

        ordering = ["-date", "station"]
        get_latest_by = ["date", "station"]

        constraints = [
            models.UniqueConstraint(
                fields=["station", "date"], name="unique_station_date_combination"
            )
        ]

    def __str__(self):
        return str(self.station.id_eess) + ", " + str(self.date)

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, StationPrice)
            and self.station == __value.station
            and self.date == __value.date
            and self.price_goa == __value.price_goa
            and self.price_g95e5 == __value.price_g95e5
            and self.price_g98e5 == __value.price_g98e5
            and self.price_glp == __value.price_glp
        )
