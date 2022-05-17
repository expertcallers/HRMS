from django.apps import AppConfig


class AmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ams'

    def ready(self):
        from jobs import updater
        updater.startfun()
        
