# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_default_user(apps, schema_editor):
    """
    Mevcut null user değerlerini admin kullanıcısına atar.
    """
    StudySession = apps.get_model('tracker', 'StudySession')
    User = apps.get_model('auth', 'User')
    
    # Admin kullanıcısını bul veya ilk kullanıcıyı al
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.first()
    
    if admin_user:
        StudySession.objects.filter(user__isnull=True).update(user=admin_user)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0002_studysession_user'),
    ]

    operations = [
        migrations.RunPython(set_default_user),
        migrations.AlterField(
            model_name='studysession',
            name='user',
            field=models.ForeignKey(
                help_text='Çalışma oturumunun sahibi kullanıcı',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='study_sessions',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Kullanıcı'
            ),
        ),
    ]

