from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from gas.models import Station


class AWTUser(User):
    """
    Model for storing users
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.username

    saved_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    saved_query = models.JSONField(
        verbose_name=_("Preferred query"),
        blank=True,
        default=dict,
    )

    is_upgraded = models.BooleanField(
        verbose_name=_("Upgraded"),
        default=False,
    )

    upgrade_uuid = models.CharField(
        verbose_name=_("Upgrade UUID"),
        max_length=24,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator("^[a-f0-9]{6}-[a-f0-9]{10}-[a-f0-9]{6}$", "Invalid UUID")
        ],
    )

    class Meta:
        verbose_name = _("AWT User")
        verbose_name_plural = _("AWT Users")

        ordering = ["username"]
