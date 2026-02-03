"""
studytracker projesi için WSGI yapılandırması.

WSGI çağrılabilirini ``application`` adlı modül seviyesinde bir değişken olarak açığa çıkarır.

Bu dosya hakkında daha fazla bilgi için:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studytracker.settings')

application = get_wsgi_application()
