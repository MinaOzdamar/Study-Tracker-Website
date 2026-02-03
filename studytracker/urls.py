"""
studytracker projesi için URL yapılandırması.

`urlpatterns` listesi URL'leri view'lere yönlendirir. Daha fazla bilgi için:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Örnekler:
Fonksiyon view'ları
    1. Import ekle:  from my_app import views
    2. urlpatterns'e URL ekle:  path('', views.home, name='home')
Sınıf tabanlı view'lar
    1. Import ekle:  from other_app.views import Home
    2. urlpatterns'e URL ekle:  path('', Home.as_view(), name='home')
Başka bir URLconf dahil etme
    1. include() fonksiyonunu import et: from django.urls import include, path
    2. urlpatterns'e URL ekle:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django yönetim paneli
    path('', include('tracker.urls')),  # Tracker uygulamasının URL'lerini dahil et
]
