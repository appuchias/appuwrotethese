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

from datetime import date

from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from gas import forms, query_handler


def search(request: HttpRequest):
    return render(
        request,
        "gas/search.html",
        {
            "form": forms.SearchStations,
        },
    )


def result(request: HttpRequest):
    if request.method not in ["GET", "POST"]:
        return HttpResponseNotAllowed(["GET", "POST"], "Method not allowed")

    form = forms.SearchStations(
        request.GET if request.method == "GET" else request.POST
    )

    if not form.is_valid():
        messages.error(request, _("Invalid form. Please try again."))
        return render(request, "gas/noresults.html", {"results": []})

    form_data = form.cleaned_data
    prices = query_handler.process_search(request, form_data)

    prices_date = form_data.get("query_date", date.today())
    if prices_date == date.today():
        prices_date = query_handler.get_last_update(form_data)

    return render(
        request,
        "gas/results.html",
        {"results": prices, "last_update": prices_date},
    )
