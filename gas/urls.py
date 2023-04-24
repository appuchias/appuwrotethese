from django.urls import path
from gas import views

urlpatterns = [
    path("", views.search),
    path("resultados/", views.result),
    # path("save/<int:id>", views.save),
]
