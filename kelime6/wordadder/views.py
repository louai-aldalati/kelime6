from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from .models import Word, WordSample
from dashboard.models import UserWordProgress
# Create your views here.




@login_required
def wordList(request):
    # 1) جلب كل الكلمات للمستخدم الحالي مع الأمثلة مسبقاً (Prefetch)
    words = (
        Word.objects
            .filter(user=request.user)
            .prefetch_related('wordsample_set')
            .order_by('-created_at')  # اختياري: للتّرتيب الأحدث أولاً
    )
    return render(request, 'wordadder/wordList.html',{'words': words,})


@login_required
def wordAdd(request):
    if request.method == 'POST':
        # 1. استخراج الحقول من request.POST و request.FILES
        eng = request.POST.get('eng_word')
        tur = request.POST.get('tur_word')
        picture = request.FILES.get('picture')  # ملف الصورة
        voice   = request.FILES.get('voice')    # ملف الصوت

        # 2. إنشاء سجل Word وربطه بالمستخدم الحالي
        word = Word.objects.create(
            user=request.user,
            eng_word=eng,
            tur_word=tur,
            picture=picture,
            voice=voice
        )

        # 3. إنشاء سجلات WordSample لكل حقل يبدأ بـ sample_
        for key, text in request.POST.items():
            if key.startswith('sample_') and text.strip():
                WordSample.objects.create(
                    word=word,
                    samples=text.strip()
                )
        # 4. إنشاء سجل UserWordProgress بالقيم المطلوبة
        UserWordProgress.objects.create(
            user=request.user,
            word=word,
            repetition_count=0,
            last_review=None,
            next_review=timezone.now().date() + timedelta(days=1)
        )

        # 4. إعادة التوجيه بعد الحفظ
        return redirect('/wordadder')  # غيّر 'words:list' إلى اسم الـ URL المناسب

    # GET
    return render(request, 'wordadder/wordAdd.html')

@login_required
def wordDetails(request, pk):
    word = get_object_or_404(Word, pk=pk, user=request.user)

    if request.method == 'POST':
        # --- تحديث حقول الكلمة ---
        word.eng_word = request.POST.get('eng_word', word.eng_word)
        word.tur_word = request.POST.get('tur_word', word.tur_word)
        if 'picture' in request.FILES:
            word.picture = request.FILES['picture']
        if 'voice' in request.FILES:
            word.voice = request.FILES['voice']
        word.save()

        # --- معالجة جمل العيِّنات ---
        # نجمع كل الحقول المسماة "samples" (ستأتي كقائمة)
        samples = request.POST.getlist('samples')
        # نحذف القديم
        word.wordsample_set.all().delete()
        # وننشئ جديد فقط للنصوص غير الفارغة
        for text in samples:
            if text.strip():
                WordSample.objects.create(word=word, samples=text.strip())

        return redirect('wordList')

    return render(request, 'wordadder/wordDetails.html', {
        'word': word,
    })


@login_required
def wordDelete(request, pk):
    # تأكد أن المستخدم يملك هذا الكائن
    word = get_object_or_404(Word, pk=pk, user=request.user)

    if request.method == 'POST':
        word.delete()
        return redirect('wordList')   # تأكد من وجود هذا الاسم في urls.py لقائمة الكلمات

    # اختياري: صفحة تأكيد الحذف
    return render(request, 'wordadder/wordList.html',)