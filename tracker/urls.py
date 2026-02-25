"""
Tracker uygulaması için URL yapılandırması.
"""
from django.urls import path
from django.views.generic import RedirectView
from . import views

# Uygulama adı (namespace için)
app_name = 'tracker'

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='root'),  # Root URL login'e yönlendir
    path('home/', views.index, name='index'),  # Ana sayfa (giriş gerekli)
    path('login/', views.login_view, name='login'),  # Giriş ve kayıt sayfası
    path('logout/', views.logout_view, name='logout'),  # Çıkış
    path('study-tracking/', views.study_tracking, name='study_tracking'),  # Çalışma Takibi sayfası
    path('study-tracking/edit/<int:session_id>/', views.edit_session, name='edit_session'),  # Kayıt düzenleme
    path('study-tracking/delete/<int:session_id>/', views.delete_session, name='delete_session'),  # Kayıt silme
    path('study/', views.study, name='study'),  # Ders Çalış sayfası
    path('todo/', views.todo_list, name='todo_list'),  # Yapılacaklar listesi sayfası
    path('todo/edit/<int:todo_id>/', views.edit_todo, name='edit_todo'),  # Görev düzenleme
    path('statistics/', views.statistics, name='statistics'),  # İstatistikler sayfası
    path('calendar/', views.calendar_view, name='calendar'),  # Takvim sayfası
    path('calendar/add-event/', views.calendar_add_event, name='calendar_add_event'),
    path('calendar/edit-event/<int:event_id>/', views.calendar_edit_event, name='calendar_edit_event'),
    path('calendar/delete-event/<int:event_id>/', views.calendar_delete_event, name='calendar_delete_event'),
]

