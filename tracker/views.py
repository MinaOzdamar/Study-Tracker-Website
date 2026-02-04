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
from .models import StudySession, TodoItem
from .forms import StudySessionForm, TodoForm

def login_view(request):
    """
    Kullanıcı giriş ve kayıt sayfası view'ı.
    
    GET isteğinde giriş ve kayıt formlarını gösterir.
    POST isteğinde kullanıcı girişi veya kayıt işlemini yapar.
    """
    # Eğer kullanıcı zaten giriş yapmışsa ana sayfaya yönlendir
    if request.user.is_authenticated:
        return redirect('tracker:index')
    
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
    
    # Bugünkü çalışma süresini saat ve dakika formatına çevir
    today_hours = today_total_duration // 60
    today_minutes = today_total_duration % 60
    
    # Streak bilgisi (şimdilik 0 olarak gösterilecek)
    # İleride ardışık günlerde çalışma yapılıp yapılmadığını kontrol edebiliriz
    streak = 0
    
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
    
    # Streak bilgisi (şimdilik 0 olarak gösterilecek)
    # İleride ardışık günlerde çalışma yapılıp yapılmadığını kontrol edebiliriz
    streak = 0
    
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
    pending_todos = total_todos - completed_todos
    
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
    
    if request.method == 'POST':
        form = StudySessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Çalışma kaydı başarıyla güncellendi!')
            return redirect('tracker:study_tracking')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = StudySessionForm(instance=session)
    
    context = {
        'form': form,
        'session': session,
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
    
    if request.method == 'POST':
        # POST isteğinde kaydı sil
        # Silmeden önce kaydın tarihini al (redirect için)
        session_date = session.date
        session.delete()
        messages.success(request, 'Çalışma kaydı başarıyla silindi!')
        # Silinen kaydın tarihine yönlendir
        return redirect(f"{reverse('tracker:study_tracking')}?date={session_date.strftime('%Y-%m-%d')}")
    
    # GET isteğinde silme onay sayfasını göster
    context = {
        'session': session,
    }
    
    return render(request, 'tracker/delete_session.html', context)
