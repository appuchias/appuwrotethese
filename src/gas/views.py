from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from appuwrotethese import extras
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
        return render(
            request,
            "gas/noresults.html",
            {"error": _("Invalid form data. Please try again."), "results": []},
        )

    form_data = form.cleaned_data
    results, product_name = query_handler.process_search(request, form_data)
    last_update = query_handler.get_last_update(form_data)

    # Show notification in case no results are returned
    if not results:
        messages.error(request, _("No results found"))
        return redirect("/gas/")

    return render(
        request,
        "gas/results.html",
        {
            "product": product_name,
            "results": results,
            "last_update": last_update,
        },
    )
