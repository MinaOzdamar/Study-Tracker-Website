"""
studytracker projesi için ASGI yapılandırması.

ASGI çağrılabilirini ``application`` adlı modül seviyesinde bir değişken olarak açığa çıkarır.

Bu dosya hakkında daha fazla bilgi için:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studytracker.settings')

application = get_asgi_application()
