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

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from gas.models import Station


class AWTUser(User):
    """Model for storing users"""

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
