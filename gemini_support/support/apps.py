from django.apps import AppConfig


def ready(self):
    import gemini_support.support.signals


class SupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'support'
