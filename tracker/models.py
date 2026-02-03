from django.db import models
from django.contrib.auth.models import User


class StudySession(models.Model):
    """
    Çalışma oturumu modeli.
    
    Bu model, kullanıcının yaptığı her bir çalışma oturumunu temsil eder.
    Her kayıt, bir ders için harcanan süreyi, tarihi ve 
    isteğe bağlı notları saklar.
    """
    
    # Kullanıcı - çalışma oturumunun sahibi
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Kullanıcı',
        help_text='Çalışma oturumunun sahibi kullanıcı',
        related_name='study_sessions'
    )
    
    # Ders adı - hangi ders için çalışma yapıldığını belirtir
    subject = models.CharField(
        max_length=125,
        verbose_name='Ders Adı',
        help_text='Çalışma yapılan dersin adı'
    )
    
    # Süre - çalışma süresini dakika cinsinden tutar
    duration = models.IntegerField(
        verbose_name='Süre (Dakika)',
        help_text='Çalışma süresi dakika cinsinden'
    )
    
    # Tarih - çalışma oturumunun yapıldığı tarih
    date = models.DateField(
        verbose_name='Tarih',
        help_text='Çalışma oturumunun yapıldığı tarih'
    )
    
    # Not - çalışma hakkında ek bilgiler (isteğe bağlı)
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='Not',
        help_text='Çalışma hakkında ek notlar (isteğe bağlı)'
    )
    
    # Oluşturulma zamanı - kaydın ne zaman oluşturulduğunu otomatik olarak tutar
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Zamanı',
        help_text='Kaydın oluşturulduğu tarih ve saat'
    )
    
    # Güncellenme zamanı - kaydın ne zaman güncellendiğini otomatik olarak tutar
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Güncellenme Zamanı',
        help_text='Kaydın son güncellendiği tarih ve saat'
    )
    
    class Meta:
        """
        Model meta bilgileri.
        """
        verbose_name = 'Çalışma Oturumu'  # Tekil isim
        verbose_name_plural = 'Çalışma Oturumları'  # Çoğul isim
        ordering = ['-date', '-created_at']  # Tarihe göre azalan sıralama (en yeni önce)
    
    def get_duration_hours(self):
        """
        Süreyi saat ve dakika formatında döndürür.
        """
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0:
            return f"{hours} saat {minutes} dakika"
        return f"{minutes} dakika"
    
    def __str__(self):
        """
        Modelin string temsili.
        Admin panelinde ve diğer yerlerde nasıl görüneceğini belirler.
        """
        return f"{self.subject} - {self.date} ({self.duration} dakika)"


class TodoItem(models.Model):
    """
    Yapılacaklar listesi öğesi modeli.
    
    Bu model, kullanıcının yapılacaklar listesindeki her bir görevi temsil eder.
    Her görev, başlık ve tamamlanma durumu bilgilerini saklar.
    """
    
    # Kullanıcı - görevin sahibi
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Kullanıcı',
        help_text='Görevin sahibi kullanıcı',
        related_name='todo_items'
    )
    
    # Başlık - görevin başlığı
    title = models.CharField(
        max_length=100,
        verbose_name='Başlık',
        help_text='Görevin başlığı'
    )
    
    # Tamamlanma durumu - görevin tamamlanıp tamamlanmadığını belirtir
    completed = models.BooleanField(
        default=False,
        verbose_name='Tamamlandı',
        help_text='Görevin tamamlanma durumu'
    )
    
    # Oluşturulma zamanı - görevin ne zaman oluşturulduğunu otomatik olarak tutar
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Zamanı',
        help_text='Görevin oluşturulduğu tarih ve saat'
    )
    
    # Güncellenme zamanı - görevin ne zaman güncellendiğini otomatik olarak tutar
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Güncellenme Zamanı',
        help_text='Görevin son güncellendiği tarih ve saat'
    )
    
    # Düzenlenme durumu - görevin başlığının düzenlenip düzenlenmediğini belirtir
    is_edited = models.BooleanField(
        default=False,
        verbose_name='Düzenlendi',
        help_text='Görevin başlığının düzenlenip düzenlenmediği'
    )
    
    # Önemli görev durumu - görevin önemli olup olmadığını belirtir
    is_important = models.BooleanField(
        default=False,
        verbose_name='Önemli',
        help_text='Görevin önemli olup olmadığı'
    )
    
    # Önemli işaretlenme zamanı - görevin ne zaman önemli olarak işaretlendiğini belirtir
    important_marked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Önemli İşaretlenme Zamanı',
        help_text='Görevin önemli olarak işaretlendiği tarih ve saat'
    )
    
    class Meta:
        """
        Model meta bilgileri.
        """
        verbose_name = 'Yapılacaklar Öğesi'  # Tekil isim
        verbose_name_plural = 'Yapılacaklar Öğeleri'  # Çoğul isim
        ordering = ['-created_at']  # Oluşturulma zamanına göre azalan sıralama (en yeni önce)
    
    def __str__(self):
        """
        Modelin string temsili.
        Admin panelinde ve diğer yerlerde nasıl görüneceğini belirler.
        """
        status = "✓" if self.completed else "○"
        return f"{status} {self.title}"
