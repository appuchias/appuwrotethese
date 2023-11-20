# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django.contrib import admin

from mastermind.models import Game, Guess


class GameAdmin(admin.ModelAdmin):
    list_display = ("game_id", "created", "user", "won", "lost")
    list_filter = ("won", "lost", "user")
    search_fields = ("game_id", "user")
    readonly_fields = ("game_id", "created", "user", "won", "lost")


class GuessAdmin(admin.ModelAdmin):
    list_display = ("game", "guess", "correct", "misplaced", "created")
    search_fields = ("game",)
    readonly_fields = ("game", "guess", "correct", "misplaced", "created")


class GuessInline(admin.TabularInline):
    model = Guess
    readonly_fields = ("guess", "correct", "misplaced", "created")


admin.site.register(Game, GameAdmin)
admin.site.register(Guess, GuessAdmin)
