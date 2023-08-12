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

from django.urls import path
from gas import views

urlpatterns = [
    path("", views.search),
    path("results/", views.result),
    path("localities/", views.names, kwargs={"q_type": "locality"}),
    path("provinces/", views.names, kwargs={"q_type": "province"}),
    # path("save/<int:id>", views.save),
]
