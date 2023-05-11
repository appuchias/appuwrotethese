from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponseNotAllowed
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
        return render(
            request,
            "gas/noresults.html",
            {"error": _("Invalid form data. Please try again."), "results": []},
        )

    form_data = form.cleaned_data
    last_update = query_handler.get_last_update(form_data)
    results, product_name = query_handler.process_search(request, form_data)

    # Show notification in case no results are returned
    if not results:
        messages.warning(request, _("No results found. Please try again."))
        raise Http404()

    return render(
        request,
        "gas/results.html",
        {
            "product": product_name,
            "results": results,
            "last_update": last_update,
        },
    )
