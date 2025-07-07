from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from .models import UserWordProgress,DailyPerformance
# Create your views here.

@login_required
def dashboard(request):
    # تاريخ اليوم
    today = timezone.now().date()

    # 1. نجمع عدد السجلات لكل قيمة من repetition_count
    qs = UserWordProgress.objects.filter(user=request.user)
    agg = qs.values('repetition_count').annotate(total=Count('id'))

    # 2. نبني قائمة أعداد مكوّنة من 6 عناصر (للدرجات 0→5)
    rep_counts = [0] * 6
    for entry in agg:
        idx = entry['repetition_count']
        if 0 <= idx < 6:
            rep_counts[idx] = entry['total']

    # 3. نحسب عدد الكلمات المستحقة اليوم (next_review <= اليوم)
    due_count = qs.filter(next_review__lte=today).count()
    
    # 3. جلب بيانات الأداء اليومي
    perf = (
        DailyPerformance.objects
        .filter(user=request.user, date=today)
        .aggregate(
            total_correct=Sum('correct'),
            total_incorrect=Sum('incorrect')
        )
    )
    total_correct = perf['total_correct'] or 0
    total_incorrect = perf['total_incorrect'] or 0
    total_answers = total_correct + total_incorrect

    # 4. حساب النسب (مع حماية القسمة على صفر)
    if total_answers > 0:
        correct_pct = round((total_correct / total_answers) * 100)
        incorrect_pct = 100 - correct_pct
    else:
        correct_pct = incorrect_pct = 0


    # 5. تمرير كل المتغيرات إلى القالب
    return render(request, 'dashboard/dashboard.html', {
        'rep_counts': rep_counts,
        'due_count': due_count,
        'correct_pct': correct_pct,
        'incorrect_pct': incorrect_pct,
    })
