from gas.models import Locality, Province, Station
from gas.helper_data import get_localities, get_provinces, fetch_data


# ###############################
# Data transfer related function
# ###############################
def _create_complementary_tables() -> None:
    """
    Update the side tables (gas_locality and gas_province) with the data from the API.
    """

    print("[·] Updating complementary tables...")

    localities = get_localities()
    provinces = get_provinces()

    if Locality.objects.count() != len(localities):
        print("  [·] Updating localities...")
        Locality.objects.bulk_create(
            [
                Locality(id_mun=locality["IDMunicipio"], name=locality["Municipio"])
                for locality in localities
            ]
        )

    if Province.objects.count() != len(provinces):
        print("  [·] Updating provinces...")
        Province.objects.bulk_create(
            [
                Province(id_prov=province["IDPovincia"], name=province["Provincia"])
                for province in provinces  # Typo in the original data
            ]
        )

    print("[✓] Updated complementary tables.")


def update_db() -> None:
    """
    Load the data from the API into the database.
    """

    stations = sorted(fetch_data()["ListaEESSPrecio"], key=lambda x: int(x["IDEESS"]))
    stations_len = len(stations)

    # Update localities and provinces
    _create_complementary_tables()

    # Change station fields to match the database
    changes = {
        "IDEESS": "id_eess",
        "Dirección": "address",
        "Horario": "schedule",
        "Rótulo": "company",
        "Latitud": "latitude",
        "Longitud (WGS84)": "longitude",
        "Precio Gasoleo A": "gasoleo_a",
        "Precio Gasolina 95 E5": "gasolina_95",
        "Precio Gasolina 98 E5": "gasolina_98",
        "Precio Gases licuados del petróleo": "glp",
        "C.P.": "postal_code",
    }
    rm_fields = [
        "Localidad",
        "Municipio",
        "Provincia",
        "Margen",
        "Precio Biodiesel",
        "Precio Bioetanol",
        "Precio Gas Natural Comprimido",
        "Precio Gas Natural Licuado",
        "Precio Gasoleo B",
        "Precio Gasoleo Premium",
        "Precio Gasolina 95 E10",
        "Precio Gasolina 95 E5 Premium",
        "Precio Gasolina 98 E10",
        "Precio Hidrogeno",
        "Remisión",
        "Tipo Venta",
        "% BioEtanol",
        "% Éster metílico",
        "IDCCAA",
    ]
    fuels = [
        "gasoleo_a",
        "gasolina_95",
        "gasolina_98",
        "glp",
    ]
    stations_to_create: list[Station] = []
    stations_to_update: list[Station] = []

    for idx, station in enumerate(stations):
        # Modify or remove fields
        for key in list(station.keys()):
            if key in changes:
                station[changes.get(key)] = station.pop(key)
            elif key in rm_fields:
                station.pop(key)

        for fuel in fuels:
            station[fuel] = float(
                (station[fuel] if station[fuel] else "0").replace(",", ".")
            )

        # Add the complementary fields
        print(
            f"  [·] Clasifying station {idx}/{stations_len}",
            end=" ",
        )
        locality = Locality.objects.filter(
            id_mun=int(station.pop("IDMunicipio"))
        ).first()
        province = Province.objects.filter(
            id_prov=int(station.pop("IDProvincia"))
        ).first()

        # Determine if the station has to be created or updated
        station_new = Station(locality=locality, province=province, **station)
        station_obj = Station.objects.filter(id_eess=station["id_eess"])
        if not station_obj:
            stations_to_create.append(station_new)
            print(" [C]", end="\r")
        elif station_new != station_obj.first():
            stations_to_update.append(station_new)
            print(" [U]", end="\r")

    print("[✓] Clasified stations." + " " * 20)
    print(f"    {len(stations_to_create)} stations to create.")
    print(f"    {len(stations_to_update)} stations to update.")

    # Create the stations
    if len(stations_to_create) > 0:
        print("[·] Creating stations...", end="\r")
        Station.objects.bulk_create(stations_to_create)
        print("[✓] Created stations.   ")

    # Update the stations
    if len(stations_to_update) > 0:
        print("[·] Updating stations...", end="\r")
        Station.objects.bulk_update(
            stations_to_update,
            list(changes.values())[1:]  # Remove id_eess
            + ["locality", "province"],  # Add locality and province
        )
        print("[✓] Updated stations.")

    print("---\n[✓] All stations refreshed.")
