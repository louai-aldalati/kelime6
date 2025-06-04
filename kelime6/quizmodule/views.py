import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizItem
from dashboard.models import UserWordProgress, DailyPerformance
from wordadder.models import Word
from settings.models import Setting
# Create your views here.

@login_required
def quizDashboard(request):
    days = 27
    today = date.today()
    # نجمع عدد العناصر لكل يوم من اليوم وحتى اليوم+27
    counts = [
        UserWordProgress.objects.filter(
            user=request.user,
            next_review=today + timedelta(days=i)
        ).count()
        for i in range(days + 1)
    ]
    return render(request, 'quizmodule/quizDashboard.html', {
        'counts': counts
    })

# جدولة خطوات المراجعة (أيام)
REVIEW_STEPS = [1, 7, 30, 90, 180, 365]

@login_required
def quizQuestion(request):
    # عند أول دخول ننشئ اختبار جديد
    if request.method == 'GET' and 'quiz_id' not in request.session:
        quiz = Quiz.objects.create(user=request.user)
        request.session['quiz_id'] = quiz.id
        # جلب الإعدادات الخاصة بالمستخدم
        user_setting = Setting.objects.get(user=request.user)
        max_questions = user_setting.quiz_size
        today = date.today()
        progresses = UserWordProgress.objects.filter(
            user=request.user,
            next_review__lte=today
        )
        if not progresses.exists():
            return redirect('quizDashboard')
        # جمع جميع المعرفات وفرزها عشوائياً
        question_ids = list(progresses.values_list('word_id', flat=True))
        random.shuffle(question_ids)

        # حصر عدد الأسئلة بحسب الإعدادات
        question_ids = question_ids[:max_questions]
        
        request.session['question_ids'] = question_ids
        request.session['question_index'] = 0
        request.session['total_questions'] = len(question_ids)

    quiz_id = request.session.get('quiz_id')
    question_ids = request.session.get('question_ids', [])
    index = request.session.get('question_index', 0)
    total_questions = request.session.get('total_questions', 0)
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    today = date.today()

    # معالجة الإرسال
    if request.method == 'POST':
        word_id = request.POST.get('question_id')
        word = get_object_or_404(Word, id=word_id, user=request.user)
        selected_text = request.POST.get('answer')
        is_correct = (selected_text == word.tur_word)
        # حفظ نتيجة السؤال
        QuizItem.objects.create(quiz=quiz, word=word, correct=is_correct)

        # تحديث UserWordProgress
        progress = UserWordProgress.objects.get(user=request.user, word=word)
        if is_correct:
            progress.repetition_count = min(progress.repetition_count + 1, len(REVIEW_STEPS) - 1)
        else:
            progress.repetition_count = 0
        progress.last_review = today
        # ضبط next_review بحسب خطوة التكرار
        days_ahead = REVIEW_STEPS[progress.repetition_count]
        progress.next_review = today + timedelta(days=days_ahead)
        progress.save()

        # تحديث DailyPerformance
        perf, created = DailyPerformance.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'correct': 0, 'incorrect': 0}
        )
        if is_correct:
            perf.correct += 1
        else:
            perf.incorrect += 1
        perf.save()

        # الانتقال للسؤال التالي
        index += 1
        if index >= total_questions:
            quiz.taken_date = today
            quiz.save()
            # تنظيف الجلسة
            for key in ['quiz_id', 'question_ids', 'question_index', 'total_questions']:
                request.session.pop(key, None)
            return redirect('quizSummary')
        request.session['question_index'] = index

    # جلب الكلمة التالية وعرضها
    word_id = question_ids[index]
    word = get_object_or_404(Word, id=word_id, user=request.user)
    distractors = Word.objects.filter(user=request.user).exclude(id=word.id).order_by('?')[:3]
    options = [word.tur_word] + [d.tur_word for d in distractors]
    random.shuffle(options)

    return render(request, 'quizmodule/quizQuestion.html', {
        'questionNumber': index + 1,
        'totalQuestions': total_questions,
        'word': word,
        'options': options,
    })



@login_required
def quizSummary(request):
    user = request.user
    today = timezone.now().date()

    # احضار أداء اليوم
    perf = DailyPerformance.objects.filter(user=user, date=today).first()
    if perf and (perf.correct + perf.incorrect) > 0:
        correct_pct = round(perf.correct / (perf.correct + perf.incorrect) * 100)
        incorrect_pct = 100 - correct_pct
    else:
        correct_pct = 0
        incorrect_pct = 0

    # احضار Quiz لليوم والعناصر المرتبطة به
    quiz = Quiz.objects.filter(user=user, taken_date=today).last()
    items = []
    if quiz:
        quiz_items = QuizItem.objects.filter(quiz=quiz)
        for qi in quiz_items:
            items.append({
                'word': qi.word.eng_word,
                'correct': qi.correct
            })

    # تمرير البيانات للـ template
    context = {
        'correct_pct': correct_pct,
        'incorrect_pct': incorrect_pct,
        'items': items,
    }
    return render(request, 'quizmodule/quizSummary.html', context)


@login_required
def quizHistory(request):
    performances = DailyPerformance.objects.filter(user=request.user).order_by('-date')
    history = []
    for perf in performances:
        total = perf.correct + perf.incorrect
        if total > 0:
            correct_pct = int(round(perf.correct * 100.0 / total))
            incorrect_pct = 100 - correct_pct
        else:
            correct_pct = incorrect_pct = 0
        history.append({
            'date': perf.date,
            'correct_pct': correct_pct,
            'incorrect_pct': incorrect_pct,
        })
    return render(request, 'quizmodule/quizHistory.html', {
        'history': history,
    })