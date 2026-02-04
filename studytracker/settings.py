"""
Django ayarları studytracker projesi için.

Django 5.2.8 kullanılarak 'django-admin startproject' komutu ile oluşturuldu.

Bu dosya hakkında daha fazla bilgi için:
https://docs.djangoproject.com/en/5.2/topics/settings/

Tüm ayarlar ve değerleri için:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje içindeki yolları şu şekilde oluştur: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Hızlı başlangıç geliştirme ayarları - üretim için uygun değil
# https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/ adresine bakın

# GÜVENLİK UYARISI: üretimde kullanılan gizli anahtarı gizli tutun!
# SECRET_KEY artık .env dosyasından okunuyor
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-)@=8ll7)lk1tk2rrvr&9u(avr-v_8tlljdikdwj(6032olqp&5')

# GÜVENLİK UYARISI: üretimde debug modunu açık bırakmayın!
# DEBUG artık .env dosyasından okunuyor
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = []


# Uygulama tanımı

INSTALLED_APPS = [
    'django.contrib.admin',  # Django yönetim paneli
    'django.contrib.auth',  # Kimlik doğrulama sistemi
    'django.contrib.contenttypes',  # İçerik türü çerçevesi
    'django.contrib.sessions',  # Oturum yönetimi
    'django.contrib.messages',  # Mesajlaşma çerçevesi
    'django.contrib.staticfiles',  # Statik dosya yönetimi
    'tracker',  # Ders takibi uygulaması
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Güvenlik middleware'i
    'django.contrib.sessions.middleware.SessionMiddleware',  # Oturum middleware'i
    'django.middleware.common.CommonMiddleware',  # Ortak middleware
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF koruması
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Kimlik doğrulama middleware'i
    'django.contrib.messages.middleware.MessageMiddleware',  # Mesaj middleware'i
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking koruması
]

# Ana URL yapılandırması
ROOT_URLCONF = 'studytracker.urls'

# Şablon yapılandırması
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Ek şablon dizinleri
        'APP_DIRS': True,  # Uygulama dizinlerinde şablon arama
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # İstek context processor'ı
                'django.contrib.auth.context_processors.auth',  # Kimlik doğrulama context processor'ı
                'django.contrib.messages.context_processors.messages',  # Mesaj context processor'ı
            ],
        },
    },
]

# WSGI uygulaması
WSGI_APPLICATION = 'studytracker.wsgi.application'


# Veritabanı yapılandırması
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL veritabanı motoru
        'NAME': os.getenv('DB_NAME', 'studytracker_db'),  # Veritabanı adı - .env dosyasından okunuyor
        'USER': os.getenv('DB_USER', 'postgres'),  # Veritabanı kullanıcı adı - .env dosyasından okunuyor
        'PASSWORD': os.getenv('DB_PASSWORD', ''),  # Veritabanı şifresi - .env dosyasından okunuyor
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Veritabanı sunucu adresi - .env dosyasından okunuyor
        'PORT': os.getenv('DB_PORT', '5432'),  # Veritabanı bağlantı portu - .env dosyasından okunuyor
    }
}


# Şifre doğrulama
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # Minimum uzunluk doğrulayıcısı
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # Sayısal şifre doğrulayıcısı
    },
]


# Uluslararasılaştırma
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'tr'  # Türkçe dil kodu

TIME_ZONE = 'Europe/Istanbul'  # İstanbul saat dilimi

USE_I18N = True  # Uluslararasılaştırmayı etkinleştir

USE_TZ = True  # Zaman dilimi desteğini etkinleştir


# Statik dosyalar (CSS, JavaScript, Resimler)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'  # Statik dosyalar için URL

# Giriş yapılmamış kullanıcılar için yönlendirilecek URL
# Kullanıcı giriş gerektiren bir sayfaya gitmeye çalışırsa buraya yönlendirilir
LOGIN_URL = '/login/'  # Giriş sayfası URL'i
LOGIN_REDIRECT_URL = '/'  # Giriş yaptıktan sonra yönlendirilecek sayfa

# Varsayılan birincil anahtar alan türü
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Otomatik artan büyük tamsayı alanı
