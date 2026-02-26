from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from datetime import timedelta
from .models import StudySession, TodoItem, CalendarEvent
from .forms import StudySessionForm, TodoForm


def calculate_streak(user):
    """
    Kullanıcının streak sayısını hesaplar.
    Üst üste en az 1 saat (60 dakika) çalışılan gün sayısını döndürür.
    """
    today = timezone.now().date()
    streak = 0
    current_date = today
    
    while True:
        # Bu günün toplam çalışma süresini hesapla
        day_sessions = StudySession.objects.filter(
            user=user,
            date=current_date
        )
        day_total_duration = day_sessions.aggregate(
            total=Sum('duration')
        )['total'] or 0
        
        # Eğer bu gün en az 1 saat (60 dakika) çalışılmışsa streak'e ekle
        if day_total_duration >= 60:
            streak += 1
            # Bir önceki güne geç
            current_date = current_date - timedelta(days=1)
        else:
            # Streak kırıldı, döngüden çık
            break
    
    return streak

def login_view(request):
    """
    Kullanıcı giriş ve kayıt sayfası view'ı.
    
    GET isteğinde giriş ve kayıt formlarını gösterir.
    POST isteğinde kullanıcı girişi veya kayıt işlemini yapar.
    """
    login_form = None
    signup_form = None
    is_signup = False
    
    if request.method == 'POST':
        # Hangi form gönderildiğini kontrol et
        if 'login' in request.POST:
            # Giriş formu gönderildi
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Hoş geldiniz, {username}!')
                    return redirect('tracker:index')
                else:
                    messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
            else:
                messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
        elif 'signup' in request.POST:
            # Kayıt formu gönderildi
            signup_form = CustomUserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, f'Hoş geldiniz, {user.username}! Hesabınız başarıyla oluşturuldu.')
                return redirect('tracker:index')
            else:
                messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
                is_signup = True
    else:
        # GET isteğinde boş formlar göster
        login_form = AuthenticationForm()
        signup_form = CustomUserCreationForm()
        # URL'de signup parametresi varsa kayıt formunu göster
        if request.GET.get('mode') == 'signup':
            is_signup = True
    
    return render(request, 'tracker/login.html', {
        'login_form': login_form or AuthenticationForm(),
        'signup_form': signup_form or CustomUserCreationForm(),
        'is_signup': is_signup
    })


@login_required
def index(request):
    """
    Ana sayfa view'ı.
    
    Sadece giriş yapmış kullanıcılar erişebilir.
    Kullanıcının bugünkü çalışma süresi, streak bilgisi ve 
    son çalışma kayıtlarını gösterir.
    """
    user = request.user
    today = timezone.now().date()
    
    # Bugünkü toplam çalışma süresi (dakika cinsinden)
    today_sessions = StudySession.objects.filter(
        user=user,
        date=today
    )
    today_total_duration = today_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0
    
    # Tamamlanmamış görev sayısı
    pending_todos_count = TodoItem.objects.filter(
        user=user,
        completed=False
    ).count()
    
    # Bugünkü çalışma süresini saat ve dakika formatına çevir
    today_hours = today_total_duration // 60
    today_minutes = today_total_duration % 60
    
    # Streak bilgisi hesapla
    streak = calculate_streak(user)
    
    # Bugün çalıştıkların listesi (sadece bugünün kayıtları)
    recent_sessions = StudySession.objects.filter(
        user=user,
        date=today
    ).order_by('-created_at')
    
    # Context verileri
    context = {
        'user': user,
        'today_total_duration': today_total_duration,
        'today_hours': today_hours,
        'today_minutes': today_minutes,
        'streak': streak,
        'recent_sessions': recent_sessions,
        'pending_todos_count': pending_todos_count,
    }
    
    return render(request, 'tracker/index.html', context)


@login_required
def logout_view(request):
    """
    Kullanıcı çıkış view'ı.
    
    Kullanıcıyı sistemden çıkarır ve giriş sayfasına yönlendirir.
    """
    from django.contrib.auth import logout
    
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('tracker:login')


@login_required
def study_tracking(request):
    """
    Çalışma Takibi sayfası view'ı.
    
    Kullanıcının çalışma kayıtlarını gösterir ve 
    yeni kayıt ekleme formunu sunar.
    Tarih filtreleme ile belirli bir günün kayıtlarını gösterir.
    """
    user = request.user
    
    # URL'den tarih parametresini al (varsa)
    selected_date_str = request.GET.get('date', None)
    
    if selected_date_str:
        try:
            # Tarih string'ini date objesine çevir
            from datetime import datetime
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Geçersiz tarih formatıysa bugünü kullan
            selected_date = timezone.now().date()
    else:
        # Tarih parametresi yoksa bugünü kullan
        selected_date = timezone.now().date()
    
    # Seçili tarihe ait kayıtları getir (en yeni önce)
    sessions = StudySession.objects.filter(
        user=user,
        date=selected_date
    ).order_by('-created_at')
    
    # Bugünün tarihi
    today = timezone.now().date()
    
    # Bugünkü toplam çalışma süresi (dakika cinsinden) - her zaman bugünün değeri gösterilecek
    today_sessions = StudySession.objects.filter(
        user=user,
        date=today
    )
    today_total_duration = today_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0
    
    # Bugünkü çalışma süresini saat ve dakika formatına çevir
    today_hours = today_total_duration // 60
    today_minutes = today_total_duration % 60
    
    # Streak bilgisi hesapla (her zaman bugünün streak'i gösterilecek)
    streak = calculate_streak(user)
    
    # Yeni kayıt ekleme formu
    form = None
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            # Form geçerliyse kaydı oluştur
            session = form.save(commit=False)
            session.user = user  # Kullanıcıyı atama
            session.save()
            messages.success(request, 'Çalışma kaydı başarıyla eklendi!')
            # Kayıt eklendikten sonra o tarihin sayfasına yönlendir
            return redirect(f"{request.path}?date={session.date.strftime('%Y-%m-%d')}")
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    
    # GET isteğinde veya form hatalıysa boş form göster
    if form is None:
        form = StudySessionForm()
        # Varsayılan tarih olarak seçili tarihi (veya bugünü) ayarla
        form.fields['date'].initial = selected_date
    
    # Önceki ve sonraki tarihleri hesapla
    from datetime import timedelta
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    
    context = {
        'sessions': sessions,
        'form': form,
        'selected_date': selected_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'today': today,
        'today_total_duration': today_total_duration,
        'today_hours': today_hours,
        'today_minutes': today_minutes,
        'streak': streak,
    }
    
    return render(request, 'tracker/study_tracking.html', context)


@login_required
def study(request):
    """
    Ders Çalış sayfası view'ı.
    
    Bu sayfa kullanıcıya süre tutucu (stopwatch) ve geri sayım (countdown) 
    özellikleri sunar. Kullanıcı çalışma süresini takip edebilir.
    """
    user = request.user
    
    # Çalışma kaydı ekleme formu
    form = None
    if request.method == 'POST':
        if 'add_session' in request.POST:
            form = StudySessionForm(request.POST)
            if form.is_valid():
                session = form.save(commit=False)
                session.user = user
                session.save()
                messages.success(request, 'Çalışma kaydı başarıyla eklendi!')
                return redirect('tracker:study_tracking')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    
    # GET isteğinde veya form hatalıysa boş form göster
    if form is None:
        form = StudySessionForm()
        # Varsayılan tarih olarak bugünü ayarla
        from django.utils import timezone
        form.fields['date'].initial = timezone.now().date()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tracker/study.html', context)


@login_required
def todo_list(request):
    """
    Yapılacaklar listesi sayfası view'ı.
    
    Kullanıcının yapılacaklar listesini görüntülemesi, yeni görev eklemesi,
    görevleri tamamlaması veya silmesi için kullanılır.
    """
    user = request.user
    
    # Filtreleme parametresi (default: tarihe göre - en yeni önce)
    filter_type = request.GET.get('filter', 'date_desc')
    
    # Kullanıcının tüm görevlerini getir
    all_todos = TodoItem.objects.filter(user=user)
    
    # Önemli görevleri her zaman en üstte göster (important_marked_at'e göre en yeni önce)
    # Filtreleme ve sıralama
    if filter_type == 'date_desc':
        # Tarihe göre (en yeni önce) - default
        # Önemli görevler önce, sonra normal görevler
        all_todos = all_todos.order_by('-is_important', '-important_marked_at', 'completed', '-created_at')
    elif filter_type == 'date_asc':
        # Tersten tarihe göre (en eski önce)
        # Önemli görevler önce, sonra normal görevler
        all_todos = all_todos.order_by('-is_important', '-important_marked_at', 'completed', 'created_at')
    elif filter_type == 'pending':
        # Sadece bekleyenler (tamamlanmayanlar)
        # Önemli görevler önce, sonra normal görevler
        all_todos = all_todos.filter(completed=False).order_by('-is_important', '-important_marked_at', '-created_at')
    elif filter_type == 'completed':
        # Sadece tamamlananlar
        # Önemli görevler önce, sonra normal görevler
        all_todos = all_todos.filter(completed=True).order_by('-is_important', '-important_marked_at', '-created_at')
    
    # Sayfalama - her sayfada 10 görev
    paginator = Paginator(all_todos, 10)
    page_number = request.GET.get('page', 1)
    try:
        todos = paginator.page(page_number)
    except:
        todos = paginator.page(1)
    
    # Yeni görev ekleme formu
    form = None
    if request.method == 'POST':
        # Form gönderildiğinde
        if 'add_todo' in request.POST:
            # Yeni görev ekleme
            form = TodoForm(request.POST)
            if form.is_valid():
                todo = form.save(commit=False)
                todo.user = user
                todo.save()
                messages.success(request, 'Görev başarıyla eklendi!')
                # Yeni görev eklendiğinde ilk sayfaya yönlendir (en yeni görevler önce)
                return redirect('tracker:todo_list')
        elif 'toggle_todo' in request.POST:
            # Görev tamamlanma durumunu değiştir
            todo_id = request.POST.get('todo_id')
            try:
                todo = TodoItem.objects.get(id=todo_id, user=user)
                todo.completed = not todo.completed
                # Eğer görev tamamlandıysa önemli işaretini kaldır
                if todo.completed and todo.is_important:
                    todo.is_important = False
                    todo.important_marked_at = None
                todo.save()
                messages.success(request, 'Görev durumu güncellendi!')
            except TodoItem.DoesNotExist:
                messages.error(request, 'Görev bulunamadı!')
            # Mevcut sayfa numarasını ve filtreyi koruyarak yönlendir
            filter_by = request.GET.get('filter', 'date_desc')
            page = request.GET.get('page', 1)
            return redirect(reverse('tracker:todo_list') + f"?page={page}&filter={filter_by}")
        elif 'delete_todo' in request.POST:
            # Görev silme
            todo_id = request.POST.get('todo_id')
            filter_by = request.GET.get('filter', 'date_desc')
            page = request.GET.get('page', 1)
            try:
                todo = TodoItem.objects.get(id=todo_id, user=user)
                todo.delete()
                messages.success(request, 'Görev başarıyla silindi!')
                # Silme sonrası sayfa numarasını kontrol et
                # Eğer sayfa boş kalırsa bir önceki sayfaya git
                remaining_todos = TodoItem.objects.filter(user=user)
                if filter_type == 'pending':
                    remaining_todos = remaining_todos.filter(completed=False)
                elif filter_type == 'completed':
                    remaining_todos = remaining_todos.filter(completed=True)
                total_count = remaining_todos.count()
                current_page = int(page)
                if total_count > 0 and (current_page - 1) * 10 >= total_count and current_page > 1:
                    page = current_page - 1
            except TodoItem.DoesNotExist:
                messages.error(request, 'Görev bulunamadı!')
            # Mevcut sayfa numarasını ve filtreyi koruyarak yönlendir
            return redirect(reverse('tracker:todo_list') + f"?page={page}&filter={filter_by}")
        elif 'toggle_important' in request.POST:
            # Görev önemli durumunu değiştir
            todo_id = request.POST.get('todo_id')
            try:
                todo = TodoItem.objects.get(id=todo_id, user=user)
                todo.is_important = not todo.is_important
                if todo.is_important:
                    # Önemli yapıldıysa zamanı kaydet
                    todo.important_marked_at = timezone.now()
                else:
                    # Önemli kaldırıldıysa zamanı temizle
                    todo.important_marked_at = None
                todo.save()
                messages.success(request, 'Görev önemli durumu güncellendi!')
            except TodoItem.DoesNotExist:
                messages.error(request, 'Görev bulunamadı!')
            # Mevcut sayfa numarasını ve filtreyi koruyarak yönlendir
            filter_by = request.GET.get('filter', 'date_desc')
            page = request.GET.get('page', 1)
            return redirect(reverse('tracker:todo_list') + f"?page={page}&filter={filter_by}")
    
            # GET isteğinde veya form hatalıysa boş form göster
    if form is None:
        form = TodoForm()
    
    # İstatistikler (tüm görevler için)
    total_todos = all_todos.count()
    completed_todos = all_todos.filter(completed=True).count()
    pending_todos = all_todos.filter(completed=False).count()  # Tamamlanmamış görevler
    
    context = {
        'todos': todos,
        'form': form,
        'total_todos': total_todos,
        'completed_todos': completed_todos,
        'pending_todos': pending_todos,
        'paginator': paginator,
        'current_page': todos.number,
        'total_pages': paginator.num_pages,
        'current_filter': filter_type,
    }
    
    return render(request, 'tracker/todo.html', context)


@login_required
def edit_todo(request, todo_id):
    """
    Görev düzenleme view'ı.
    
    Kullanıcının kendi görevini düzenlemesine izin verir.
    Görevin başlığını değiştirir, oluşturulma tarihini korur ve is_edited flag'ini True yapar.
    """
    user = request.user
    
    # Görevi getir (sadece kullanıcının kendi görevi)
    todo = get_object_or_404(TodoItem, id=todo_id, user=user)
    
    # Oluşturulma tarihini sakla (created_at değişmemesi için)
    original_created_at = todo.created_at
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            # Görevin oluşturulma tarihini koru (created_at değişmeyecek)
            # is_edited flag'ini True yap
            todo_item = form.save(commit=False)
            todo_item.is_edited = True
            todo_item.created_at = original_created_at  # Oluşturulma tarihini koru
            todo_item.save()
            messages.success(request, 'Görev başarıyla güncellendi!')
            # Mevcut sayfa numarasını ve filtreyi koruyarak yönlendir
            filter_by = request.GET.get('filter', 'date_desc')
            page = request.GET.get('page', 1)
            return redirect(reverse('tracker:todo_list') + f"?page={page}&filter={filter_by}")
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = TodoForm(instance=todo)
    
    context = {
        'form': form,
        'todo': todo,
    }
    
    return render(request, 'tracker/edit_todo.html', context)


@login_required
def edit_session(request, session_id):
    """
    Çalışma kaydı düzenleme view'ı.
    
    Kullanıcının kendi çalışma kaydını düzenlemesine izin verir.
    """
    user = request.user
    
    # Kaydı getir (sadece kullanıcının kendi kaydı)
    session = get_object_or_404(StudySession, id=session_id, user=user)
    
    # URL'den veya referrer'dan tarih parametresini al
    return_date = request.GET.get('date', None)
    if not return_date:
        # Referrer'dan tarih parametresini al
        referrer = request.META.get('HTTP_REFERER', '')
        if 'date=' in referrer:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(referrer)
            params = parse_qs(parsed.query)
            if 'date' in params:
                return_date = params['date'][0]
    
    # Eğer hala tarih yoksa, kaydın tarihini kullan
    if not return_date:
        return_date = session.date.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        form = StudySessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Çalışma kaydı başarıyla güncellendi!')
            # Kaydedilen kaydın tarihine yönlendir (veya return_date'e)
            redirect_date = form.cleaned_data['date'].strftime('%Y-%m-%d')
            return redirect(f"{reverse('tracker:study_tracking')}?date={redirect_date}")
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = StudySessionForm(instance=session)
    
    context = {
        'form': form,
        'session': session,
        'return_date': return_date,
    }
    
    return render(request, 'tracker/edit_session.html', context)


@login_required
def delete_session(request, session_id):
    """
    Çalışma kaydı silme view'ı.
    
    Kullanıcının kendi çalışma kaydını silmesine izin verir.
    """
    user = request.user
    
    # Kaydı getir (sadece kullanıcının kendi kaydı)
    session = get_object_or_404(StudySession, id=session_id, user=user)
    
    # URL'den veya referrer'dan tarih parametresini al
    return_date = request.GET.get('date', None)
    if not return_date:
        # Referrer'dan tarih parametresini al
        referrer = request.META.get('HTTP_REFERER', '')
        if 'date=' in referrer:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(referrer)
            params = parse_qs(parsed.query)
            if 'date' in params:
                return_date = params['date'][0]
    
    # Eğer hala tarih yoksa, kaydın tarihini kullan
    if not return_date:
        return_date = session.date.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        # POST isteğinde kaydı sil
        # Silmeden önce kaydın tarihini al (redirect için)
        session_date = session.date
        session.delete()
        messages.success(request, 'Çalışma kaydı başarıyla silindi!')
        # Silinen kaydın tarihine yönlendir (veya return_date'e)
        redirect_date = return_date or session_date.strftime('%Y-%m-%d')
        return redirect(f"{reverse('tracker:study_tracking')}?date={redirect_date}")
    
    # GET isteğinde silme onay sayfasını göster
    context = {
        'session': session,
        'return_date': return_date,
    }
    
    return render(request, 'tracker/delete_session.html', context)


@login_required
def statistics(request):
    """
    İstatistikler sayfası view'ı.
    
    Kullanıcının çalışma ve yapılacaklar istatistiklerini gösterir.
    """
    user = request.user
    
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)
    thirty_days_ago = today - timedelta(days=29)
    
    # ==========================
    # ÇALIŞMA İSTATİSTİKLERİ
    # ==========================
    all_sessions = StudySession.objects.filter(user=user)
    
    # Günlük toplam süreleri (date -> dakika) çıkar
    date_totals_qs = (
        all_sessions
        .values('date')
        .annotate(total=Sum('duration'))
        .order_by('date')
    )
    date_totals = {row['date']: row['total'] for row in date_totals_qs}
    
    # Toplam çalışma süresi (dakika) - şimdiye kadar
    total_study_minutes = sum(date_totals.values())
    total_study_hours = total_study_minutes // 60
    total_study_remaining_minutes = total_study_minutes % 60
    
    # Toplam oturum sayısı
    total_sessions = all_sessions.count()
    
    # Çalışılan gün sayısı (en az bir kayıt olan gün)
    study_days_count = len(date_totals)
    
    # İlk ve son çalışma tarihi
    first_session = all_sessions.order_by('date').first()
    last_session = all_sessions.order_by('-date').first()
    first_study_date = first_session.date if first_session else None
    last_study_date = last_session.date if last_session else None
    
    # Çalışılan gün başına ortalama süre (şimdiye kadar)
    avg_minutes_per_study_day = 0
    if study_days_count > 0:
        avg_minutes_per_study_day = total_study_minutes // study_days_count
    
    avg_study_hours = avg_minutes_per_study_day // 60
    avg_study_minutes = avg_minutes_per_study_day % 60
    
    # Tüm günlerin ortalaması (ilk kayıt tarihinden bugüne kadar)
    total_days_avg_minutes = 0
    total_days_avg_hours = 0
    total_days_avg_remaining_minutes = 0
    if first_study_date:
        total_days = (today - first_study_date).days + 1  # +1 bugünü dahil etmek için
        if total_days > 0:
            total_days_avg_minutes = total_study_minutes // total_days
            total_days_avg_hours = total_days_avg_minutes // 60
            total_days_avg_remaining_minutes = total_days_avg_minutes % 60
    
    # En uzun çalışma seansı
    longest_session = all_sessions.order_by('-duration').first()
    longest_session_minutes = longest_session.duration if longest_session else 0
    longest_session_hours = longest_session_minutes // 60
    longest_session_remaining_minutes = longest_session_minutes % 60
    longest_session_subject = longest_session.subject if longest_session else None
    longest_session_date = longest_session.date if longest_session else None
    
    # Bugünkü çalışma
    today_sessions = all_sessions.filter(date=today)
    today_total_minutes = today_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0
    today_hours = today_total_minutes // 60
    today_minutes = today_total_minutes % 60
    today_sessions_count = today_sessions.count()
    
    # Son 7 gün çalışma (bugün dahil)
    last_7_days_sessions = all_sessions.filter(date__gte=seven_days_ago, date__lte=today)
    last_7_days_minutes = last_7_days_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0
    last_7_days_hours = last_7_days_minutes // 60
    last_7_days_remaining_minutes = last_7_days_minutes % 60
    
    # Son 30 gün çalışma (bugün dahil)
    last_30_days_sessions = all_sessions.filter(date__gte=thirty_days_ago, date__lte=today)
    last_30_days_minutes = last_30_days_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0
    last_30_days_hours = last_30_days_minutes // 60
    last_30_days_remaining_minutes = last_30_days_minutes % 60
    
    # Günlük detaylar (son 7 gün) - küçük tablo ve trend için
    last_7_days_details = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_minutes = date_totals.get(day, 0)
        last_7_days_details.append({
            'date': day,
            'minutes': day_minutes,
            'hours': day_minutes // 60,
            'remaining_minutes': day_minutes % 60,
        })
    # Trend grafikleri için maksimum değer
    last_7_days_max_minutes = max((d['minutes'] for d in last_7_days_details), default=0)
    # Yüzdeleri ekle (bar grafiği için) - orantılı olarak
    for d in last_7_days_details:
        if last_7_days_max_minutes > 0 and d['minutes'] > 0:
            d['percent'] = round((d['minutes'] / last_7_days_max_minutes) * 100, 1)
        else:
            d['percent'] = 0
    
    # Mevcut streak (zaten kullanılan fonksiyon)
    current_streak = calculate_streak(user)
    
    # En uzun streak (tüm zamanlar) - en az 60 dakika çalışılan ardışık günler
    longest_streak = 0
    current_run = 0
    prev_date = None
    for row in date_totals_qs:
        day = row['date']
        total = row['total'] or 0
        if total >= 60:
            if prev_date and day == prev_date + timedelta(days=1):
                current_run += 1
            else:
                current_run = 1
        else:
            current_run = 0
        if current_run > longest_streak:
            longest_streak = current_run
        prev_date = day
    
    # Streak geçmişi (son 30 gün için takvim verisi)
    last_30_days_streak = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        minutes = date_totals.get(day, 0)
        has_streak = minutes >= 60
        last_30_days_streak.append({
            'date': day,
            'minutes': minutes,
            'has_streak': has_streak,
        })
    
    # Streak kaybetme uyarısı: Dün 60+ dk ise ve bugün henüz 60 dk altında ise
    yesterday = today - timedelta(days=1)
    yesterday_minutes = date_totals.get(yesterday, 0)
    streak_warning = yesterday_minutes >= 60 and today_total_minutes < 60
    streak_warning_minutes_needed = max(0, 60 - today_total_minutes)
    
    # ==========================
    # ZAMAN ARALIĞI (Dropdown için)
    # ==========================
    range_param = request.GET.get('range', '7')  # '7', '14', '30', 'all'
    if range_param not in ['7', '14', '30', 'all']:
        range_param = '7'
    
    if range_param == 'all':
        range_label = 'Şimdiye Kadar'
        range_start_date = None
    else:
        days = int(range_param)
        # 7 ve 14 için "Son X Gün", 30 için "Son 1 Ay"
        if days == 30:
            range_label = 'Son 1 Ay'
        else:
            range_label = f'Son {days} Gün'
        range_start_date = today - timedelta(days=days - 1)
    
    if range_start_date:
        range_sessions = all_sessions.filter(date__gte=range_start_date, date__lte=today)
    else:
        range_sessions = all_sessions
    
    range_total_minutes = range_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0
    range_hours = range_total_minutes // 60
    range_remaining_minutes = range_total_minutes % 60
    
    range_sessions_count = range_sessions.count()
    range_days_count = range_sessions.values('date').distinct().count()
    
    range_avg_minutes = 0
    if range_days_count > 0:
        range_avg_minutes = range_total_minutes // range_days_count
    range_avg_hours = range_avg_minutes // 60
    range_avg_remaining_minutes = range_avg_minutes % 60
    
    # Genel Özet: seçilen aralığa göre ortalamalar
    if range_start_date:
        total_days_in_range = (today - range_start_date).days + 1
    else:
        total_days_in_range = (today - first_study_date).days + 1 if first_study_date else 0
    
    genel_tum_gunler_avg_minutes = (range_total_minutes // total_days_in_range) if total_days_in_range > 0 else 0
    genel_tum_gunler_hours = genel_tum_gunler_avg_minutes // 60
    genel_tum_gunler_remaining_minutes = genel_tum_gunler_avg_minutes % 60
    genel_calisilan_hours = range_avg_hours
    genel_calisilan_minutes = range_avg_remaining_minutes
    
    # ==========================
    # YAPILACAKLAR İSTATİSTİKLERİ
    # ==========================
    all_todos = TodoItem.objects.filter(user=user)
    
    total_todos = all_todos.count()
    completed_todos = all_todos.filter(completed=True).count()
    pending_todos = total_todos - completed_todos
    important_todos = all_todos.filter(is_important=True).count()
    
    # Tamamlanma oranı
    completion_rate = 0
    if total_todos > 0:
        completion_rate = round((completed_todos / total_todos) * 100)
    
    # Bugün oluşturulan görevler
    created_today_todos = all_todos.filter(created_at__date=today).count()
    
    # Bugün tamamlanan görevler
    completed_today_todos = all_todos.filter(
        completed=True,
        updated_at__date=today
    ).count()
    
    # Son 7 gün görev özeti
    last_7_days_todo_details = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_created = all_todos.filter(created_at__date=day).count()
        day_completed = all_todos.filter(completed=True, updated_at__date=day).count()
        last_7_days_todo_details.append({
            'date': day,
            'created': day_created,
            'completed': day_completed,
        })
    
    # Görev trend grafiği için maksimum tamamlanan görev sayısı
    last_7_days_todo_max_completed = max((d['completed'] for d in last_7_days_todo_details), default=0)
    for d in last_7_days_todo_details:
        if last_7_days_todo_max_completed > 0 and d['completed'] > 0:
            d['completed_percent'] = round((d['completed'] / last_7_days_todo_max_completed) * 100, 1)
        else:
            d['completed_percent'] = 0
    
    # ==========================
    # SAAT BAZLI ÇALIŞMA DAĞILIMI
    # ==========================
    # Oturumun yapıldığı saate yaklaşık olarak created_at saatine göre bakıyoruz
    hour_buckets = [
        {'label': 'Gece (00-03)', 'start': 0, 'end': 3, 'minutes': 0},
        {'label': 'Sabah (04-07)', 'start': 4, 'end': 7, 'minutes': 0},
        {'label': 'Sabah (08-11)', 'start': 8, 'end': 11, 'minutes': 0},
        {'label': 'Öğlen (12-15)', 'start': 12, 'end': 15, 'minutes': 0},
        {'label': 'Akşam (16-19)', 'start': 16, 'end': 19, 'minutes': 0},
        {'label': 'Gece (20-23)', 'start': 20, 'end': 23, 'minutes': 0},
    ]
    for session in all_sessions:
        if session.created_at:
            hour = session.created_at.hour
            for bucket in hour_buckets:
                if bucket['start'] <= hour <= bucket['end']:
                    bucket['minutes'] += session.duration
                    break
    hour_buckets_max = max((b['minutes'] for b in hour_buckets), default=0)
    for bucket in hour_buckets:
        if hour_buckets_max > 0 and bucket['minutes'] > 0:
            bucket['percent'] = round((bucket['minutes'] / hour_buckets_max) * 100, 1)
        else:
            bucket['percent'] = 0
    
    # ==========================
    # HEDEF VE MOTİVASYON
    # ==========================
    # Varsayılan hedefler: günde 60 dk, haftada 7*60 dk, ayda 30*60 dk
    daily_goal_minutes = 60
    weekly_goal_minutes = 7 * daily_goal_minutes
    monthly_goal_minutes = 30 * daily_goal_minutes
    
    weekly_progress_percent = 0
    monthly_progress_percent = 0
    if weekly_goal_minutes > 0:
        weekly_progress_percent = min(100, int((last_7_days_minutes / weekly_goal_minutes) * 100)) if last_7_days_minutes > 0 else 0
    if monthly_goal_minutes > 0:
        monthly_progress_percent = min(100, int((last_30_days_minutes / monthly_goal_minutes) * 100)) if last_30_days_minutes > 0 else 0
    
    # Başarı rozetleri / achievements
    achievements = [
        {
            'code': 'first_session',
            'title': 'İlk Adım',
            'description': 'İlk çalışma kaydını oluşturdun.',
            'earned': total_sessions >= 1,
        },
        {
            'code': 'ten_hours',
            'title': '10 Saat Kulübü',
            'description': 'Toplamda en az 10 saat çalıştın.',
            'earned': total_study_minutes >= 10 * 60,
        },
        {
            'code': 'fifty_hours',
            'title': '50 Saat Ustası',
            'description': 'Toplamda en az 50 saat çalıştın.',
            'earned': total_study_minutes >= 50 * 60,
        },
        {
            'code': 'week_streak',
            'title': '7 Günlük Seri',
            'description': 'En az 7 gün üst üste 60+ dakika çalıştın.',
            'earned': longest_streak >= 7,
        },
        {
            'code': 'hundred_sessions',
            'title': '100 Oturum',
            'description': 'En az 100 çalışma oturumu kaydettin.',
            'earned': total_sessions >= 100,
        },
    ]
    
    context = {
        'user': user,
        # Çalışma istatistikleri
        'total_study_minutes': total_study_minutes,
        'total_study_hours': total_study_hours,
        'total_study_remaining_minutes': total_study_remaining_minutes,
        'total_sessions': total_sessions,
        'study_days_count': study_days_count,
        'first_study_date': first_study_date,
        'last_study_date': last_study_date,
        'avg_study_hours': avg_study_hours,
        'avg_study_minutes': avg_study_minutes,
        'total_days_avg_hours': total_days_avg_hours,
        'total_days_avg_remaining_minutes': total_days_avg_remaining_minutes,
        'genel_tum_gunler_hours': genel_tum_gunler_hours,
        'genel_tum_gunler_remaining_minutes': genel_tum_gunler_remaining_minutes,
        'genel_calisilan_hours': genel_calisilan_hours,
        'genel_calisilan_minutes': genel_calisilan_minutes,
        'longest_session_minutes': longest_session_minutes,
        'longest_session_hours': longest_session_hours,
        'longest_session_remaining_minutes': longest_session_remaining_minutes,
        'longest_session_subject': longest_session_subject,
        'longest_session_date': longest_session_date,
        'today_total_minutes': today_total_minutes,
        'today_hours': today_hours,
        'today_minutes': today_minutes,
        'today_sessions_count': today_sessions_count,
        'last_7_days_minutes': last_7_days_minutes,
        'last_7_days_hours': last_7_days_hours,
        'last_7_days_remaining_minutes': last_7_days_remaining_minutes,
        'last_30_days_minutes': last_30_days_minutes,
        'last_30_days_hours': last_30_days_hours,
        'last_30_days_remaining_minutes': last_30_days_remaining_minutes,
        'last_7_days_details': last_7_days_details,
        'last_7_days_max_minutes': last_7_days_max_minutes,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_30_days_streak': last_30_days_streak,
        'streak_warning': streak_warning,
        'streak_warning_minutes_needed': streak_warning_minutes_needed,
        # Zaman aralığı istatistikleri
        'range_param': range_param,
        'range_label': range_label,
        'range_total_minutes': range_total_minutes,
        'range_hours': range_hours,
        'range_remaining_minutes': range_remaining_minutes,
        'range_sessions_count': range_sessions_count,
        'range_days_count': range_days_count,
        'range_avg_hours': range_avg_hours,
        'range_avg_remaining_minutes': range_avg_remaining_minutes,
        # Todo istatistikleri
        'total_todos': total_todos,
        'completed_todos': completed_todos,
        'pending_todos': pending_todos,
        'important_todos': important_todos,
        'completion_rate': completion_rate,
        'created_today_todos': created_today_todos,
        'completed_today_todos': completed_today_todos,
        'last_7_days_todo_details': last_7_days_todo_details,
        'last_7_days_todo_max_completed': last_7_days_todo_max_completed,
        # Saat bazlı dağılım
        'hour_buckets': hour_buckets,
        'hour_buckets_max': hour_buckets_max,
        # Hedefler ve motivasyon
        'daily_goal_minutes': daily_goal_minutes,
        'weekly_goal_minutes': weekly_goal_minutes,
        'monthly_goal_minutes': monthly_goal_minutes,
        'weekly_progress_percent': weekly_progress_percent,
        'monthly_progress_percent': monthly_progress_percent,
        'achievements': achievements,
    }
    
    return render(request, 'tracker/statistics.html', context)


# Takvim: depolanan renk -> pastel gösterim rengi (eski renkler için)
CALENDAR_DISPLAY_COLOR_MAP = {
    '#7f00ff': '#c9a0ff', '#667eea': '#c9a0ff',
    '#0070f9': '#8fc4ff', '#f5576c': '#8fc4ff',
    '#00ffff': '#88eeff', '#4ecdc4': '#88eeff',
    '#ed74d2': '#f5b0e6', '#45b7d1': '#f5b0e6', '#ff56ff': '#f5b0e6',
    '#6bc64d': '#b8e8a8', '#96ceb4': '#b8e8a8', '#9ed98a': '#b8e8a8',
    '#ffeaa7': '#fff0b8',
    '#ff993a': '#ffcc99', '#f8b4c4': '#ffcc99',
    '#dfe6e9': '#f8c0ed',
}


def _calendar_text_color(hex_str):
    """Hex arka plan rengine göre okunabilir metin rengi: siyah veya beyaz."""
    hex_str = (hex_str or '').strip().lstrip('#')
    if len(hex_str) != 6:
        return '#000'
    try:
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
    except ValueError:
        return '#000'
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return '#fff' if lum < 180 else '#000'


@login_required
def calendar_view(request):
    """
    Takvim sayfası. Sayfada tek ay gösterilir, ok ile ileri/geri gidilir.
    """
    from datetime import date
    from calendar import monthrange

    # Bugünü uygulama saat dilimine göre al (UTC değil, örn. Europe/Istanbul)
    now_local = timezone.localtime(timezone.now())
    today = now_local.date()
    offset = int(request.GET.get('offset', 0))  # -1: geri, 0: şimdi, 1: ileri
    year = today.year
    month = today.month + offset  # her tıklamada 1 ay kaydır
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1

    def month_days(y, m):
        first = date(y, m, 1)
        last_day = monthrange(y, m)[1]
        start_weekday = first.weekday()  # Pazartesi=0 (hafta pazartesi ile başlar)
        weeks = []
        day = 1
        week = [None] * 7
        for i in range(42):
            pos = i % 7  # hafta içindeki gün (0-6)
            if i < start_weekday and day == 1:
                week[pos] = None
            else:
                if day <= last_day:
                    week[pos] = date(y, m, day)
                    day += 1
                else:
                    week[pos] = None
            if (i + 1) % 7 == 0:
                weeks.append(week)
                week = [None] * 7
        return weeks, first

    weeks, first_day = month_days(year, month)
    month_name = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'][month]
    months_data = [{
        'year': year,
        'month': month,
        'month_name': month_name,
        'weeks': weeks,
        'first_day': first_day,
    }]

    # Etkinlikleri getir: sadece bu ay
    start = date(year, month, 1)
    end_last = monthrange(year, month)[1]
    end = date(year, month, end_last)

    events = CalendarEvent.objects.filter(
        user=request.user,
        date__gte=start,
        date__lte=end
    ).order_by('date', 'created_at')

    events_by_date = {}
    for e in events:
        key = e.date.isoformat()
        if key not in events_by_date:
            events_by_date[key] = []
        display_hex = CALENDAR_DISPLAY_COLOR_MAP.get(e.color, e.color)
        text_color = _calendar_text_color(display_hex)
        events_by_date[key].append({
            'id': e.id, 'title': e.title, 'color': e.color,
            'color_display': display_hex, 'text_color': text_color,
        })

    # Haftalardaki günlere etkinlik listesi ekle
    for week in months_data[0]['weeks']:
        for i, d in enumerate(week):
            if d is not None:
                key = d.isoformat()
                week[i] = {'date': d, 'date_iso': key, 'events': events_by_date.get(key, [])}
            else:
                week[i] = None

    context = {
        'months_data': months_data,
        'today': today.isoformat(),
        'next_offset': offset + 1,
        'prev_offset': offset - 1,
        'color_choices': CalendarEvent.COLOR_CHOICES,
    }
    return render(request, 'tracker/calendar.html', context)


@login_required
def calendar_add_event(request):
    """Bir güne takvim etkinliği (başlık/iş) ekler. AJAX POST."""
    from django.http import JsonResponse
    from datetime import datetime

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST gerekli'}, status=400)

    date_str = request.POST.get('date')
    title = (request.POST.get('title') or '').strip()
    color = request.POST.get('color', '#c9a0ff')

    if not date_str or not title:
        return JsonResponse({'ok': False, 'error': 'Tarih ve başlık gerekli'}, status=400)

    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Geçersiz tarih'}, status=400)

    allowed_colors = [c[0] for c in CalendarEvent.COLOR_CHOICES]
    if color not in allowed_colors:
        color = '#c9a0ff'

    event = CalendarEvent.objects.create(user=request.user, date=d, title=title[:100], color=color)
    return JsonResponse({
        'ok': True,
        'id': event.id,
        'title': event.title,
        'color': event.color,
        'date': event.date.isoformat(),
    })


@login_required
def calendar_edit_event(request, event_id):
    """Takvim etkinliğini günceller. AJAX POST."""
    from django.http import JsonResponse
    event = get_object_or_404(CalendarEvent, id=event_id, user=request.user)
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST gerekli'}, status=400)
    title = (request.POST.get('title') or '').strip()
    color = request.POST.get('color', event.color)
    if not title:
        return JsonResponse({'ok': False, 'error': 'Başlık gerekli'}, status=400)
    allowed_colors = [c[0] for c in CalendarEvent.COLOR_CHOICES]
    if color not in allowed_colors:
        color = event.color
    event.title = title[:100]
    event.color = color
    event.save()
    return JsonResponse({
        'ok': True,
        'id': event.id,
        'title': event.title,
        'color': event.color,
        'date': event.date.isoformat(),
    })


@login_required
def calendar_delete_event(request, event_id):
    """Takvim etkinliğini siler. AJAX POST."""
    from django.http import JsonResponse
    event = get_object_or_404(CalendarEvent, id=event_id, user=request.user)
    event.delete()
    return JsonResponse({'ok': True})
