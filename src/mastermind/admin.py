# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.contrib import admin

from mastermind.models import Game, Guess


class GuessAdmin(admin.ModelAdmin):
    list_display = ("game", "guess", "correct", "misplaced", "created")
    search_fields = ("game",)
    readonly_fields = ("game", "guess", "correct", "misplaced", "created")


class GuessInline(admin.TabularInline):
    model = Guess
    readonly_fields = ("guess", "correct", "misplaced", "created")


class GameAdmin(admin.ModelAdmin):
    list_display = ("game_id", "created", "user", "won", "finished")
    list_filter = ("won", "finished", "user")
    search_fields = ("game_id", "user")
    readonly_fields = ("game_id", "code", "created", "won", "finished")

    inlines = [GuessInline]


admin.site.register(Game, GameAdmin)
admin.site.register(Guess, GuessAdmin)
