from django.apps import AppConfig


class MyAppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_apps'

    # def ready(self):
    #     from .ap_scheduler import start
    #     start()
