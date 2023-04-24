from django.apps import AppConfig

# import threading
from gas import helper_data


class GasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gas"

    # Run code ONCE when started
    def ready(self) -> None:
        helper_data.create_files()
