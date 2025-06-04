from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Setting

# Create your views here.

@login_required
def settings(request):
    # جلب أو إنشاء سجل الإعدادات للمستخدم الحالي
    setting, created = Setting.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # قراءة القيمة المدخلة من النموذج
        try:
            new_size = int(request.POST.get('quiz_size', setting.quiz_size))
        except ValueError:
            messages.error(request, 'Lütfen Geçerli Bir Sayı Giriniz.')
            return redirect('settings')

        # حفظ التغيير ضمن حدود الـ validators في الـ model
        setting.quiz_size = new_size
        setting.save()
        messages.success(request, 'Her Bir Testteki Kelime Sayısı Başarıyla Güncellendi.')
        return redirect('settings')

    # عند الـ GET فقط، مرّر قيمة setting إلى القالب
    return render(request, 'settings/settings.html', {
        'settings': setting
    })