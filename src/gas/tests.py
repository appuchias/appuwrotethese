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

from gas.db_actions import create_localities_provinces, get_data, update_station_prices
from gas.query_handler import get_ids

LOCALITY_NAME = "Madrid"
LOCALITY_ID = 4354
PROVINCE_NAME = "Madrid"
PROVINCE_ID = 28
POSTAL_CODE = "28005"
FUEL_ABBR = "G95E5"
FUEL_NAME = "gasolina 95"

FUELS = {
    "GOA": "diésel",
    "G95E5": "gasolina 95",
    "G98E5": "gasolina 98",
    "GLP": "gas licuado del petróleo",
}


class GasSearch(TestCase):
    """Test the gas search view.

    Things tested:
        - The view is reachable (status code 200).
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
        - The view returns the correct fuel
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up the test database."""

        create_localities_provinces()
        update_station_prices(SAMPLE_DATA)

    def test_view(self):
        """Test that the results view is reachable."""

        response = self.client.post("/gas/results/")
        self.assertEqual(response.status_code, 200)

    def test_results_rejects_invalid_methods(self):
        """Test that the results view rejects invalid methods."""

        response = self.client.get("/gas/results/")
        self.assertEqual(response.status_code, 405)

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

    def test_results_rejects_invalid_form_data(self):
        """Test that the results view rejects invalid form data."""

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "locality",
                "fuel_abbr": "GOA",
                "q_date": date.today() + timedelta(days=1),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "locality",
                "fuel_abbr": "GOA",
                "q_date": date.today() - timedelta(days=1),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "locality",
                "fuel_abbr": "GOA",
                "q_date": "invalid",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "locality",
                "fuel_abbr": "GOA",
                "q_date": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "locality",
                "fuel_abbr": "invalid",
                "q_date": date.today(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "invalid",
                "fuel_abbr": "GOA",
                "q_date": date.today(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": "",
                "q_type": "locality",
                "fuel_abbr": "GOA",
                "q_date": date.today(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["results"], [])

    def test_results_correct_results(self):
        """Test that the results view returns the correct results."""

        response = self.client.post("/gas/results/")
        self.assertEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": LOCALITY_NAME,
                "q_type": "locality",
                "fuel_abbr": FUEL_ABBR,
                "q_date": date.today(),
            },
        )
        self.assertNotEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": PROVINCE_NAME,
                "q_type": "province",
                "fuel_abbr": FUEL_ABBR,
                "q_date": date.today(),
            },
        )
        self.assertNotEqual(response.context["results"], [])

        response = self.client.post(
            "/gas/results/",
            {
                "term": POSTAL_CODE,
                "q_type": "postal_code",
                "fuel_abbr": FUEL_ABBR,
                "q_date": date.today(),
            },
        )
        self.assertNotEqual(response.context["results"], [])

    def test_results_correct_fuel(self):
        """Test that the results view returns the correct product name."""

        for fuel_abbr, fuel_name in FUELS.items():
            response = self.client.post(
                "/gas/results/",
                {
                    "term": LOCALITY_NAME,
                    "q_type": "locality",
                    "fuel_abbr": fuel_abbr,
                    "q_date": date.today(),
                },
            )

            self.assertEqual(response.context["fuel"], fuel_name)


class GasQueryHandlerTests(TestCase):
    """Test the gas query handler.

    Things tested:
        - The handler returns the correct product name
        - The handler returns the correct last update date
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up the test database."""

        create_localities_provinces()
        update_station_prices(get_data()["ListaEESSPrecio"])

    def test_ids(self):
        """Test that the query handler returns the correct product name."""

        self.assertEqual(get_ids(LOCALITY_NAME, "locality")[0], LOCALITY_ID)
        self.assertEqual(get_ids(PROVINCE_NAME, "province")[1], PROVINCE_ID)
        self.assertEqual(get_ids(str(POSTAL_CODE), "postal_code")[2], int(POSTAL_CODE))


class GasListsTests(TestCase):
    """Test the gas lists view.

    Things tested:
        - The view is reachable (status code 200) with GET
        - The view rejects invalid methods
        - The view returns the correct results
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up the test database."""

        create_localities_provinces()

    def test_localities(self):
        response = self.client.get("/gas/localities/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Madrid")

    def test_provinces(self):
        response = self.client.get("/gas/provinces/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Madrid")

    def test_invalid_methods(self):
        response = self.client.post("/gas/localities/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/gas/localities/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/gas/localities/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/gas/localities/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/gas/localities/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/gas/localities/")
        self.assertEqual(response.status_code, 405)

        response = self.client.post("/gas/provinces/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/gas/provinces/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/gas/provinces/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/gas/provinces/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/gas/provinces/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/gas/provinces/")
        self.assertEqual(response.status_code, 405)


SAMPLE_DATA = [
    {
        "C.P.": "28008",
        "Direcci\u00f3n": "PASEO MORET, 7",
        "Horario": "L-V: 07:30-21:00; S: 09:00-14:00",
        "Latitud": "40,432861",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,724194",
        "Margen": "I",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,569",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,625",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,699",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "dm",
        "R\u00f3tulo": "CEPSA",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "10943",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28005",
        "Direcci\u00f3n": "CALLE SEGOVIA C/V A PASEO VIRGEN DEL PUERTO, S/N",
        "Horario": "L-V: 07:00-22:00; S: 08:00-22:00; D: 09:00-21:00",
        "Latitud": "40,413778",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,721472",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,559",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,649",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,699",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "dm",
        "R\u00f3tulo": "CEPSA",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4520",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28005",
        "Direcci\u00f3n": "CL PASEO ACACIAS, 8",
        "Horario": "L-D: 24H",
        "Latitud": "40,404417",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,705389",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,509",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,819",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "3217",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28005",
        "Direcci\u00f3n": "RONDA SEGOVIA, 37",
        "Horario": "L-V: 06:00-23:45; S-D: 07:00-23:00",
        "Latitud": "40,410250",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,717528",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,549",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,605",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "1,739",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "CEPSA",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "3213",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28015",
        "Direcci\u00f3n": "CALLE ALBERTO AGUILERA, 18",
        "Horario": "L-D: 24H",
        "Latitud": "40,430000",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,708500",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,489",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,569",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,799",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "SHELL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4711",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28015",
        "Direcci\u00f3n": "CALLE ALBERTO AGUILERA, 9",
        "Horario": "L-D: 24H",
        "Latitud": "40,429694",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,708389",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "0,939",
        "Precio Gasoleo A": "1,489",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,589",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,819",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4352",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28012",
        "Direcci\u00f3n": "GLORIETA EMBAJADORES, 0",
        "Horario": "L-V: 07:30-22:00; S: 08:00-14:30",
        "Latitud": "40,405278",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,703139",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,539",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,649",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,699",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "dm",
        "R\u00f3tulo": "CEPSA",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4508",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28012",
        "Direcci\u00f3n": "BARRIO CENTRO-EMBAJADORES, 83",
        "Horario": "L-D: 24H",
        "Latitud": "40,401833",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,699694",
        "Margen": "I",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,519",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,599",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,649",
        "Precio Gasolina 95 E5 Premium": "1,719",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,789",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "dm",
        "R\u00f3tulo": "CEPSA",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "3164",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28055",
        "Direcci\u00f3n": "CALLE FRANCISCO UMBRAL, 2",
        "Horario": "L-D: 24H",
        "Latitud": "40,473861",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,624556",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "0,909",
        "Precio Gasoleo A": "1,529",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,694",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,834",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "SHELL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "12694",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28055",
        "Direcci\u00f3n": "GLORIETA JOSE LUIS FERNANDEZ DEL AMO, SN",
        "Horario": "L-D: 06:00-00:00",
        "Latitud": "40,485139",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,642806",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,519",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,599",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,679",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,819",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "SHELL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "13621",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28055",
        "Direcci\u00f3n": "AVENIDA FRANCISCO JAVIER SAENZ DE OIZA, ESQUINA GLORIETA JUAN DE HARO, 5",
        "Horario": "L-D: 06:00-00:00",
        "Latitud": "40,497972",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,626444",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,529",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,694",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,834",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "SHELL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "13653",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28045",
        "Direcci\u00f3n": "PASEO SANTA MARIA DE LA CABEZA, 90",
        "Horario": "L-D: 24H",
        "Latitud": "40,397722",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,702472",
        "Margen": "N",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,504",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,584",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,639",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,779",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "SHELL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4717",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28045",
        "Direcci\u00f3n": "PASEO SANTA MARIA DE LA CABEZA, 18",
        "Horario": "L-D: 24H",
        "Latitud": "40,405639",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,695250",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,509",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,819",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "3218",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28045",
        "Direcci\u00f3n": "CL PLAZA LEGAZPI, 9",
        "Horario": "L-D: 24H",
        "Latitud": "40,391361",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,695306",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,509",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,819",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4531",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28045",
        "Direcci\u00f3n": "CL ANCORA 39",
        "Horario": "L-V: 08:00-15:00",
        "Latitud": "40,402944",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,689556",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,509",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4501",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28031",
        "Direcci\u00f3n": "CARRETERA M-203 KM. 0,28",
        "Horario": "S: 09:00-14:00",
        "Latitud": "40,379944",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,596139",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "0,929",
        "Precio Gasoleo A": "1,519",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,579",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,649",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,769",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4611",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28031",
        "Direcci\u00f3n": "CARRETERA M-203 KM. 0,28",
        "Horario": "L-V: 07:00-14:00; S: 09:00-14:00",
        "Latitud": "40,380250",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,597667",
        "Margen": "I",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "",
        "Precio Gasoleo A": "1,519",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,579",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,649",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,769",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "4616",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
    {
        "C.P.": "28031",
        "Direcci\u00f3n": "CALLE REAL DE ARGANDA, 74",
        "Horario": "L-D: 24H",
        "Latitud": "40,375750",
        "Localidad": "MADRID",
        "Longitud (WGS84)": "-3,604056",
        "Margen": "D",
        "Municipio": "Madrid",
        "Precio Biodiesel": "",
        "Precio Bioetanol": "",
        "Precio Gas Natural Comprimido": "",
        "Precio Gas Natural Licuado": "",
        "Precio Gases licuados del petr\u00f3leo": "0,929",
        "Precio Gasoleo A": "1,529",
        "Precio Gasoleo B": "",
        "Precio Gasoleo Premium": "1,609",
        "Precio Gasolina 95 E10": "",
        "Precio Gasolina 95 E5": "1,659",
        "Precio Gasolina 95 E5 Premium": "",
        "Precio Gasolina 98 E10": "",
        "Precio Gasolina 98 E5": "1,789",
        "Precio Hidrogeno": "",
        "Provincia": "MADRID",
        "Remisi\u00f3n": "OM",
        "R\u00f3tulo": "REPSOL",
        "Tipo Venta": "P",
        "% BioEtanol": "0,0",
        "% \u00c9ster met\u00edlico": "0,0",
        "IDEESS": "11472",
        "IDMunicipio": "4354",
        "IDProvincia": "28",
        "IDCCAA": "13",
    },
]
