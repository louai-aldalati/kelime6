from django.shortcuts import render
from django.http import JsonResponse
from dashboard.models import DailyPerformance,UserWordProgress
from django.contrib.auth.decorators import login_required
from quizmodule.models import Quiz,QuizItem
from datetime import date, timedelta


# Create your views here.
def reportsList(request):
    return render(request, 'reports/reportsList.html')


@login_required
def dailyPerformance(request):
    # إذا وصلنا طلب AJAX بالـ query params
    start = request.GET.get('start')
    end   = request.GET.get('end')

    if start is not None or end is not None:
        qs = DailyPerformance.objects.filter(user=request.user)
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        data = list(qs.order_by('-date').values('date', 'correct', 'incorrect'))
        return JsonResponse(data, safe=False)

    # طلب عادي: عرض الصفحة مع البيانات الافتراضية
    from datetime import date, timedelta
    today = date.today()
    one_month_ago = today - timedelta(days=30)

    performances = DailyPerformance.objects.filter(
        user=request.user,
        date__gte=one_month_ago,
        date__lte=today
    ).order_by('-date')

    context = {
        'performances': performances,
        'start_date': one_month_ago.isoformat(),
        'end_date': today.isoformat(),
    }
    return render(request, 'reports/dailyPerformance.html', context)




@login_required
def difficultWords(request):
    threshold = request.GET.get('threshold')
    if threshold is not None:
        try:
            threshold = int(threshold)
        except ValueError:
            threshold = 0
        qs = UserWordProgress.objects.filter(
            user=request.user,
            repetition_count__lt=threshold
        )
        data = []
        for up in qs:
            data.append({
                'word': up.word.eng_word,
                'repetition_count': up.repetition_count,
                'last_review': up.last_review.isoformat() if up.last_review else '',
                'next_review': up.next_review.isoformat(),
            })
        return JsonResponse(data, safe=False)
    return render(request, 'reports/difficultWords.html')


@login_required
def quizSessions(request):
    # استقبال باراميترز التاريخ من GET
    start = request.GET.get('start')
    end   = request.GET.get('end')

    # إذا أتى الطلب مع start أو end نرجع JSON
    if start is not None or end is not None:
        qs = Quiz.objects.filter(user=request.user)
        if start:
            qs = qs.filter(taken_date__gte=start)
        if end:
            qs = qs.filter(taken_date__lte=end)

        data = []
        for quiz in qs.order_by('-taken_date'):
            items = QuizItem.objects.filter(quiz=quiz)
            total = items.count()
            correct = items.filter(correct=True).count()
            data.append({
                'taken_at': quiz.taken_date.isoformat() if quiz.taken_date else '',
                'total_questions': total,
                'correct_count': correct,
            })
        return JsonResponse(data, safe=False)

    # طلب عادي: عرض القالب مع نطاق افتراضي (آخر شهر)
    today = date.today()
    one_month_ago = today - timedelta(days=30)
    context = {
        'start_date': one_month_ago.isoformat(),
        'end_date': today.isoformat(),
    }
    return render(request, 'reports/quizSessions.html', context)

