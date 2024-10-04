from django.apps import AppConfig


class AirServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'air_service'

    def ready(self):
        import air_service.signals
