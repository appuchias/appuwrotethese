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

from datetime import date, datetime, timedelta
from django.test import TestCase

from gas import db_actions


class GasSearch(TestCase):
    """Test the gas search view.

    Tests the view is reachable (status code 200).
    """

    def test_search(self):
        """Test that the search view is reachable."""
        response = self.client.get("/gas/")
        self.assertEqual(response.status_code, 200)


class GasResults(TestCase):
    """Test the gas results view.

    Things tested:
        - The view is reachable (status code 200) with GET and POST
        - The view rejects invalid methods
        - The view rejects invalid form data
        - The view returns the correct results
        - The view returns the correct product name
        - The view returns the correct last update date
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up the test database."""

        db_actions.update_db()

    def test_results(self):
        """Test that the results view is reachable."""

        response = self.client.get("/gas/results/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/gas/results/")
        self.assertEqual(response.status_code, 200)

    def test_results_rejects_invalid_methods(self):
        """Test that the results view rejects invalid methods."""

        response = self.client.put("/gas/results/")
        self.assertEqual(response.status_code, 405)

        response = self.client.delete("/gas/results/")
        self.assertEqual(response.status_code, 405)

        response = self.client.patch("/gas/results/")
        self.assertEqual(response.status_code, 405)

        response = self.client.head("/gas/results/")
        self.assertEqual(response.status_code, 405)

        response = self.client.options("/gas/results/")
        self.assertEqual(response.status_code, 405)

    def test_results_correct_results(self):
        """Test that the results view returns the correct results."""

        response = self.client.post("/gas/results/")
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GOA", "show_all": True},
        )
        self.assertGreater(len(response.context["results"]), 0)

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GOA", "show_all": False},
        )
        self.assertGreater(len(response.context["results"]), 0)

    def test_results_correct_product(self):
        """Test that the results view returns the correct product name."""

        response = self.client.get(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GOA", "show_all": True},
        )
        self.assertEqual(response.context["product"], "Gasóleo A")

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "G95E5", "show_all": True},
        )
        self.assertEqual(response.context["product"], "Gasolina 95")

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "G98E5", "show_all": True},
        )
        self.assertEqual(response.context["product"], "Gasolina 98")

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GLP", "show_all": True},
        )
        self.assertEqual(response.context["product"], "GLP")

        # And with show_all = False
        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GOA", "show_all": False},
        )
        self.assertEqual(response.context["product"], "Gasóleo A")

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "G95E5", "show_all": False},
        )
        self.assertEqual(response.context["product"], "Gasolina 95")

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "G98E5", "show_all": False},
        )
        self.assertEqual(response.context["product"], "Gasolina 98")

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GLP", "show_all": False},
        )
        self.assertEqual(response.context["product"], "GLP")

    def test_results_correct_last_update(self):
        """Test that the results view returns the correct last update date."""

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GOA", "show_all": True},
        )
        self.assertGreater(
            response.context["last_update"], date.today().strftime("%d-%m-%Y")
        )

        response = self.client.post(
            "/gas/results/",
            {"query": "Madrid", "type": "locality", "fuel": "GOA", "show_all": False},
        )
        self.assertGreater(
            response.context["last_update"],
            (datetime.now() - timedelta(minutes=1)).strftime("%d-%m-%Y"),
        )
