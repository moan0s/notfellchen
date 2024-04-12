from django.apps import AppConfig
from .tools.signals import ensure_groups
from django.db.models.signals import post_migrate

class FellchensammlungConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fellchensammlung'

    def ready(self):
        post_migrate.connect(ensure_groups, sender=self)
