# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>

from django import forms


class MastermindGuess(forms.Form):
    game_id = forms.IntegerField(required=True)
    guess = forms.IntegerField(required=True)
