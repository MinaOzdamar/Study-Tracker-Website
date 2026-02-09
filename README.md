# Study-Tracker-Website
Studie - Çalışma Takip ve Yönetim Platformu

Django ve PostgreSQL kullanılarak geliştirilen, kullanıcıya özel çalışma süresi takibi ve görev yönetimi yapabilen modern web uygulaması.

Özellikler

📚 Çalışma Takibi
- Süre tutucu (stopwatch) ve geri sayım (countdown) ile çalışma süresi ölçümü
- Ders bazlı çalışma kayıtları oluşturma ve yönetme
- Tarih bazlı çalışma geçmişi görüntüleme
- Sayfa değişikliklerinde bile çalışmaya devam eden timer'lar (localStorage)

📋 Yapılacaklar Listesi
- Görev ekleme, düzenleme ve silme
- Görevleri tamamlanmış/tamamlanmamış olarak işaretleme
- Önemli görevleri işaretleme
- Tamamlanmamış görev sayısı takibi

📊 İstatistikler ve Analiz
- Günlük toplam çalışma süresi takibi
- Streak sistemi
- Görev istatistikleri

🔐 Kullanıcı Yönetimi
- Güvenli kullanıcı kayıt ve giriş sistemi
- Kullanıcıya özel veri yönetimi
- Modern ve kullanıcı dostu arayüz

Teknolojiler

Backend:
- Python 3.13.3
- Django 5.2.8
- PostgreSQL
- Django ORM
- Django Authentication

Frontend:
- HTML5
- CSS3
- JavaScript (Vanilla JS)
- localStorage API

Diğer:
- python-dotenv (Ortam değişkenleri yönetimi)
- psycopg2-binary (PostgreSQL bağlantısı)
