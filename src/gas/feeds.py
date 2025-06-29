# Appu Wrote These
# Copyright (C) 2025  Appuchia <appuchia@appu.ltd>

from datetime import datetime, time, timedelta
from django.contrib.syndication.views import Feed
from django.urls import reverse
from gas.models import StationPrice, Station, Locality, Province


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
        return reverse("station", kwargs={"id_eess": item.station.id_eess})

    def item_guid(self, item):
        return f"{item.station.id_eess}_{item.date.isoformat()}"

    def item_pubdate(self, item):
        return datetime.combine(item.date, time(0, 0, 0))


class FuelAreaFeed(Feed):
    item_count = 3
    language = "es"
    link = "/gas/"
    ttl = 360

    fuel = None

    def get_object(self, request, fuel, area):
        self.fuel = fuel.lower()

        locality = Locality.objects.filter(name__iexact=area).first()
        if locality:
            return locality

        province = Province.objects.filter(name__iexact=area.upper()).first()
        if province:
            return province

        return None

    def title(self, obj):
        if isinstance(obj, Locality) or isinstance(obj, Province):
            return f"Últimos precios de combustible en {obj.name}"

        return "Últimos precios de combustible"

    def description(self, obj):
        if isinstance(obj, Locality):
            return f"Últimos precios de combustible en {obj.name}."
        elif isinstance(obj, Province):
            return f"Últimos precios de combustible en la provincia de {obj.name}."

        return "Últimos precios de combustible."

    def items(self, obj):
        """Get the items for the feed."""

        if isinstance(obj, Locality):
            stations = Station.objects.filter(locality=obj)
        elif isinstance(obj, Province):
            stations = Station.objects.filter(province=obj)
        else:
            return list()

        prices = (
            StationPrice.objects.filter(
                station__in=stations,
                date__isnull=False,
                date__gt=datetime.now().date() - timedelta(days=self.item_count),
            )
            .exclude(**{f"price_{self.fuel}": None})
            .order_by("-date", f"price_{self.fuel}")
        )

        if not prices.exists():
            return list()

        return prices

    def item_title(self, item):
        title = f"{item.station.company}: "

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
            return title + "Ningún precio disponible"

        return title + " | ".join(f"{text} {price}€" for text, price in prices)

    def item_description(self, item):
        description = f"Precios en {item.station.company} {item.station.address}, {item.station.locality.name}, {item.station.province.name}:<br/><br/>"

        prices = list(
            filter(
                lambda x: x[1],
                [
                    ("Gasóleo A", item.price_goa),
                    ("Gasóleo B", item.price_gob),
                    ("Gasolina 95 E5", item.price_g95e5),
                    ("Gasolina 95 E5 Premium", item.price_g95e5_premium),
                    ("Gasolina 95 E10", item.price_g95e10),
                    ("Gasolina 98 E5", item.price_g98e5),
                    ("Gasolina 98 E10", item.price_g98e10),
                    ("GLP", item.price_glp),
                    ("GNC", item.price_gnc),
                    ("Hidrógeno", item.price_h2),
                ],
            )
        )
        if not prices:
            return description + "Ningún precio disponible"

        return description + "<br/>".join(f"{text} {price}€" for text, price in prices)

    def item_link(self, item):
        return reverse("station", kwargs={"id_eess": item.station.id_eess})

    def item_guid(self, item):
        return f"{item.station.id_eess}_{item.date.isoformat()}"

    def item_pubdate(self, item):
        return datetime.combine(item.date, time(0, 0, 0))
