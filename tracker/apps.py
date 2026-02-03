from django.apps import AppConfig


class TrackerConfig(AppConfig):
    """
    Tracker uygulaması yapılandırması.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # Varsayılan otomatik alan türü
    name = 'tracker'  # Uygulama adı
