from django.contrib import admin
from .models import StudySession

# Modellerinizi buraya kaydedin.

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    """
    StudySession modeli için gelişmiş admin panel yapılandırması.
    
    Bu yapılandırma ile çalışma oturumları admin panelinde
    kolayca görüntülenebilir, aranabilir, filtrelenebilir ve sıralanabilir.
    """
    
    # Liste görünümünde gösterilecek alanlar
    # Bu alanlar admin panelindeki liste sayfasında sütunlar olarak görünür
    list_display = ['user', 'subject', 'duration', 'date', 'note']
    
    # Liste görünümünde tıklanabilir olacak alanlar (detay sayfasına götürür)
    # Ders adına tıklayarak kayıt detayına gidilebilir
    list_display_links = ['subject']
    
    # Liste görünümünde sıralanabilir alanlar
    # Bu alanların başlıklarına tıklayarak sıralama yapılabilir
    list_editable = []  # Şu an için düzenlenebilir alan yok
    
    # Filtreleme seçenekleri (sağ tarafta filtre paneli)
    # Tarihe ve kullanıcıya göre filtreleme yapılabilir
    list_filter = ['date', 'user']
    
    # Arama yapılabilecek alanlar (üstteki arama kutusu)
    # Sadece ders adına göre arama yapılabilir
    search_fields = ['subject']
    
    # Tarih bazlı hiyerarşik filtreleme (üstte tarih navigasyonu)
    # Yıl, ay, gün bazında filtreleme yapılabilir
    date_hierarchy = 'date'
    
    # Varsayılan sıralama (en yeni tarih önce)
    # Kayıtlar tarihe göre en yeniden eskiye sıralanır
    ordering = ['-date']
    
    # Detay sayfası için alan grupları (daha okunabilir form)
    # Form alanları mantıksal gruplara ayrılmıştır
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('user', 'subject', 'date', 'duration'),
            'description': 'Çalışma oturumunun temel bilgileri'
        }),
        ('Ek Bilgiler', {
            'fields': ('note',),
            'description': 'Çalışma hakkında ek notlar (isteğe bağlı)',
            'classes': ('collapse',)  # Varsayılan olarak daraltılmış
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'description': 'Kayıt oluşturulma ve güncellenme zamanları',
            'classes': ('collapse',)  # Varsayılan olarak daraltılmış
        }),
    )
    
    # Sadece okunabilir alanlar (düzenlenemez)
    # Bu alanlar otomatik olarak oluşturulduğu için düzenlenemez
    readonly_fields = ['created_at', 'updated_at']
    
    # Liste görünümünde sayfa başına gösterilecek kayıt sayısı
    list_per_page = 25
    
    # Liste görünümünde maksimum gösterilecek kayıt sayısı
    list_max_show_all = 100
