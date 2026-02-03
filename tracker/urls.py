"""
Tracker uygulaması için URL yapılandırması.
"""
from django.urls import path
from . import views

# Uygulama adı (namespace için)
app_name = 'tracker'

urlpatterns = [
    path('', views.index, name='index'),  # Ana sayfa (giriş gerekli)
    path('login/', views.login_view, name='login'),  # Giriş sayfası
    path('signup/', views.signup_view, name='signup'),  # Kayıt sayfası
    path('logout/', views.logout_view, name='logout'),  # Çıkış
    path('study-tracking/', views.study_tracking, name='study_tracking'),  # Çalışma Takibi sayfası
    path('study-tracking/edit/<int:session_id>/', views.edit_session, name='edit_session'),  # Kayıt düzenleme
    path('study-tracking/delete/<int:session_id>/', views.delete_session, name='delete_session'),  # Kayıt silme
    path('study/', views.study, name='study'),  # Ders Çalış sayfası
    path('todo/', views.todo_list, name='todo_list'),  # Yapılacaklar listesi sayfası
    path('todo/edit/<int:todo_id>/', views.edit_todo, name='edit_todo'),  # Görev düzenleme
]

