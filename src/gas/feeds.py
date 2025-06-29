# Appu Wrote These
# Copyright (C) 2025  Appuchia <appuchia@appu.ltd>

from datetime import datetime, time
from django.contrib.syndication.views import Feed
from django.urls import reverse
from gas.models import StationPrice, Station


class StationFeed(Feed):
    item_count = 7
    language = "es"
    ttl = 360

    def get_object(self, request, id_eess):
        return Station.objects.get(id_eess=id_eess)

    def title(self, obj):
        return f"Últimos precios de {obj.company}"

    def description(self, obj):
        return f"Últimos precios de combustible en la estación {obj.company} ({obj.id_eess}) de {obj.locality.name}, {obj.province.name}."

    def link(self, obj):
        return reverse("station", kwargs={"id_eess": obj.id_eess})

    def items(self, obj):
        return StationPrice.objects.filter(station=obj).order_by("-date")[
            : self.item_count
        ]

    def item_title(self, item):
        prices = list(
            filter(
                lambda x: x[1] is not None,
                [
                    ("Gasóleo A", item.price_goa),
                    ("Gasolina 95 E5", item.price_g95e5),
                    ("GLP", item.price_glp),
                ],
            )
        )
        if not prices:
            return "Ningún precio disponible"

        return " | ".join(f"{text} {price}€" for text, price in prices)

    def item_description(self, item):
        prices = list(
            filter(
                lambda x: x[1],
                [
                    ("Gasóleo B", item.price_gob),
                    ("Gasolina 95 E5 Premium", item.price_g95e5_premium),
                    ("Gasolina 95 E10", item.price_g95e10),
                    ("Gasolina 98 E5", item.price_g98e5),
                    ("Gasolina 98 E10", item.price_g98e10),
                    ("GNC", item.price_gnc),
                    ("Hidrógeno", item.price_h2),
                ],
            )
        )
        if not prices:
            return "Sin precios adicionales"

        return " | ".join(f"{text} {price}€" for text, price in prices)

    def item_link(self, item):
        return "/gas/station/{}/".format(item.station.id_eess)

    def item_guid(self, item):
        return f"{item.station.id_eess}_{item.date.isoformat()}"

    def item_pubdate(self, item):
        return datetime.combine(item.date, time(0, 0, 0))
