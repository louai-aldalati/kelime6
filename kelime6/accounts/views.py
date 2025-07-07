from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
# Create your views here.
def signIn(request):
    if request.method == 'POST':
        # جلب البيانات من الـ POST
        username = request.POST.get('username')
        password = request.POST.get('password')

        # تحقق من تعبئة الحقول الأساسية
        if not username or not password:
            messages.error(request, "Kullanıcı adı ve parola girilmesi zorunludur.")
        else:
            # تأكيد بيانات الدخول
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # تسجيل الدخول وإنشاء الجلسة
                login(request, user)
                messages.success(request, f"{username} olarak başarıyla giriş yaptınız.")
                return redirect('/dashboard')
            else:
                messages.error(request, "Kullanıcı adı veya parola hatalı.")

    # عند GET أو عند حدوث خطأ في POST نعيد عرض صفحة تسجيل الدخول
    return render(request, 'accounts/signIn.html')

def signUp(request):
    if request.method == 'POST':
        # جلب البيانات من الـ POST
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')

        # تحقق من تعبئة الحقول الأساسية
        if not username or not email or not password:
            messages.error(request, "Tüm alanların doldurulması zorunludur.")
        # تحقق من عدم وجود مستخدم بنفس الاسم مسبقاً
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor. Lütfen başka bir ad seçin.")
        else:
            # إنشاء المستخدم وتشفير كلمة المرور تلقائياً
            data = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, f"Kullanıcı {data.username} başarıyla oluşturuldu.")
            return redirect('/')  # غيِّر المسار إن لزم

    # عند GET أو عند ظهور خطأ نعيد عرض النموذج في الصفحة
    return render(request, 'accounts/signUp.html')
    

def resetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Lütfen e-posta adresinizi girin.')
            return render(request, 'accounts/resetPassword.html')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Bu e-posta kayıtlı değil.')
            return render(request, 'accounts/resetPassword.html')

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={
                'uidb64': uidb64,
                'token': token
            })
        )

        subject = 'Şifre Sıfırlama Bağlantısı'
        message = (
            f'Merhaba {user.username},\n\n'
            f'Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:\n{reset_link}\n\n'
            'Bu isteği siz yapmadıysanız, bu mesajı göz ardı edebilirsiniz.'
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(request, 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.')
        return redirect('resetPassword')

    return render(request, 'accounts/resetPassword.html')