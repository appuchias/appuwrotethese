# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.contrib import admin

from gas.models import Locality, Province, Station, StationPrice


# Register your models here.
class StationAdmin(admin.ModelAdmin):
    fields = [
        ("id_eess", "company", "address"),
        ("latitude", "longitude"),
        "schedule",
        ("province", "locality", "postal_code"),
    ]
    readonly_fields = [
        "id_eess",
        "company",
        "address",
        "locality",
        "province",
        "postal_code",
    ]
    list_display = [
        "company",
        "address",
        "latitude",
        "longitude",
        "locality",
        "province",
        "postal_code",
    ]
    list_display_links = [
        "company",
        "address",
        "latitude",
        "longitude",
    ]
    list_filter = [
        "province",
    ]
    search_fields = [
        "company",
        "address",
        "locality__name",
        "province__name",
        "postal_code",
    ]


class StationInline(admin.TabularInline):
    model = Station
    fields = [
        ("id_eess", "company", "address"),
        ("latitude", "longitude"),
        "schedule",
    ]
    readonly_fields = [
        "id_eess",
        "company",
        "address",
        "locality",
        "province",
        "postal_code",
    ]
    list_display = [
        "company",
        "address",
        "latitude",
        "longitude",
    ]
    list_display_links = [
        "company",
        "address",
        "latitude",
        "longitude",
    ]
    list_filter = [
        "company",
        "locality",
        "province",
        "postal_code",
    ]
    search_fields = [
        "company",
        "address",
        "locality__name",
        "province__name",
        "postal_code",
    ]


class StationPriceAdmin(admin.ModelAdmin):
    fields = [
        "station",
        "date",
        "price_goa",
        "price_g95e5",
        "price_g98e5",
        "price_glp",
    ]
    readonly_fields = [
        "station",
        "date",
        "price_goa",
        "price_g95e5",
        "price_g98e5",
        "price_glp",
    ]
    list_display = [
        "station",
        "date",
        "price_goa",
        "price_g95e5",
        "price_g98e5",
        "price_glp",
    ]
    list_display_links = [
        "date",
        "station",
    ]
    list_filter = [
        "date",
    ]
    search_fields = [
        "date",
    ]


class StationPriceInline(admin.TabularInline):
    model = StationPrice
    fields = [
        "date",
        "station",
        "price_goa",
        "price_g95e5",
        "price_g98e5",
        "price_glp",
    ]
    readonly_fields = [
        "date",
        "station",
        "price_goa",
        "price_g95e5",
        "price_g98e5",
        "price_glp",
    ]
    list_display = [
        "date",
        "station",
        "price_goa",
        "price_g95e5",
        "price_g98e5",
        "price_glp",
    ]
    list_display_links = [
        "date",
        "station",
    ]
    list_filter = [
        "date",
    ]
    search_fields = [
        "date",
    ]


class LocalityAdmin(admin.ModelAdmin):
    fields = [
        "name",
    ]
    list_display = ["name"]
    list_display_links = ["name"]
    search_fields = ["name"]
    inlines = [StationInline]


class ProvinceAdmin(admin.ModelAdmin):
    fields = [
        "name",
    ]
    list_display = ["name"]
    list_display_links = ["name"]
    search_fields = ["name"]
    inlines = [StationInline]


admin.site.register(Locality, LocalityAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(StationPrice, StationPriceAdmin)
