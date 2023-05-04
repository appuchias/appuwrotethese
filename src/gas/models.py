from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from decimal import Decimal


class Locality(models.Model):
    """
    Model for storing localities (Added for search optimization)
    """

    id_mun = models.IntegerField(
        verbose_name=_("Municipality ID"),
        help_text=_("ID of the municipality"),
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

    gasoleo_a = models.DecimalField(
        verbose_name="Gasoleo A",
        max_digits=4,
        decimal_places=3,
        default=Decimal(0),
    )
    gasolina_95 = models.DecimalField(
        verbose_name="Gasolina 95",
        max_digits=4,
        decimal_places=3,
        default=Decimal(0),
    )
    gasolina_98 = models.DecimalField(
        verbose_name="Gasolina 98",
        max_digits=4,
        decimal_places=3,
        default=Decimal(0),
    )
    glp = models.DecimalField(
        verbose_name="GLP",
        max_digits=4,
        decimal_places=3,
        default=Decimal(0),
    )

    class Meta:
        verbose_name = _("Gas station")
        verbose_name_plural = _("Gas stations")

        ordering = ["id_eess"]

    def __str__(self):
        return self.company + ", " + self.address

    def __iter__(self):
        yield "id_eess", self.id_eess
        yield "company", self.company
        yield "address", self.address
        yield "schedule", self.schedule
        yield "locality", self.locality
        yield "province", self.province
        yield "postal_code", self.postal_code
        yield "latitude", self.latitude
        yield "longitude", self.longitude