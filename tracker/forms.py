from django import forms
from .models import StudySession, TodoItem


class StudySessionForm(forms.ModelForm):
    """
    Çalışma oturumu formu.
    
    Kullanıcıların yeni çalışma kaydı oluşturması veya 
    mevcut kayıtları düzenlemesi için kullanılır.
    """
    
    class Meta:
        model = StudySession
        fields = ['subject', 'duration', 'date', 'note']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Matematik, Fizik, Kimya...'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dakika cinsinden',
                'min': 1
            }),
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Çalışma hakkında notlar (isteğe bağlı)'
            }),
        }
        labels = {
            'subject': 'Ders Adı',
            'duration': 'Süre',
            'date': 'Tarih',
            'note': 'Not',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Not alanı için özel widget
        self.fields['note'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Çalışma hakkında notlarınızı buraya yazabilirsiniz...'
        })


class TodoForm(forms.ModelForm):
    """
    Yapılacaklar listesi formu.
    
    Kullanıcının yeni görev oluşturması veya mevcut görevi düzenlemesi için kullanılır.
    """
    
    class Meta:
        model = TodoItem
        fields = ['title']
        labels = {
            'title': 'Görev',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '',
                'maxlength': 100,
            }),
        }

