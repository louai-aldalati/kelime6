from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('',views.signIn, name='signIn'),
    path('signUp/',views.signUp, name='signUp'),
    path('resetPassword/',views.resetPassword, name='resetPassword'),
    #  مسار تأكيد إعادة التعيين
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/resetConfirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),

    #  مسار الصفحة النهائية بعد نجاح التعيين
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/resetDone.html'
        ),
        name='password_reset_complete'
    ),
]