import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models.functions import Length
from wordadder.models import Word
from dashboard.models import UserWordProgress
from .models import Puzzle, Guess, LetterFeedback
# Create your views here.
@login_required
def startWordle(request):
    if request.method == 'POST':
        word_length = int(request.POST.get('word_length'))
        max_attempts = int(request.POST.get('max_attempts'))

        # اختر كلمة عشوائية بناءً على طول eng_word
        # وقم بتصفية الكلمات التي تجاوزت 6 تكرارات لدى المستخدم الحالي
        word = (
            Word.objects
                .annotate(length=Length('eng_word'))
                .filter(
                    length=word_length,
                    userwordprogress__user=request.user,
                    userwordprogress__repetition_count=6,
                )
                .order_by('?')
                .first()
        )

        if not word:
            # يمكنك هنا التعامل مع حالة عدم وجود كلمات مناسبة
            return render(request, 'wordle/startWordle.html', {
                'message': 'Şu anda kriterlere uyan kelime bulunmamaktadır.'
            })

        puzzle = Puzzle.objects.create(
            user=request.user,
            word=word,
            word_length=word_length,
            max_attempts=max_attempts,
        )

        return redirect('boardWordle', puzzle_id=puzzle.id)

    return render(request, 'wordle/startWordle.html')


@login_required
def boardWordle(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, id=puzzle_id, user=request.user)
    context = {
        'puzzle': puzzle,
        'word_length': puzzle.word_length,
        'max_attempts': puzzle.max_attempts,
        'rows': range(puzzle.max_attempts),
        'cols': range(puzzle.word_length),
    }
    return render(request, 'wordle/boardWordle.html', context)



@login_required
@require_POST
def boardWordleGuess(request, puzzle_id):
    # استقبال طلب AJAX يحتوي على guess_text
    puzzle = get_object_or_404(Puzzle, id=puzzle_id, user=request.user)
    # قراءة البيانات المرسلة كـ JSON
    try:
        data = json.loads(request.body)
        guess_text = data['guess'].lower()
    except Exception:
        return HttpResponseBadRequest('Invalid data')

    # عدّ المحاولات الحالية
    attempt_number = Guess.objects.filter(puzzle=puzzle).count() + 1

    # إنشاء كائن Guess
    guess = Guess.objects.create(
        puzzle=puzzle,
        guess_text=guess_text,
        attempt_number=attempt_number
    )

    # تجهيز feedback لكل حرف
    target = puzzle.word.eng_word.lower()
    feedback = []
    target_chars = list(target)
    # مرحلة 1: علامة الصحيح
    for i, ch in enumerate(guess_text):
        if target_chars[i] == ch:
            feedback.append('correct')
            target_chars[i] = None  # حُجز هذا الحرف
        else:
            feedback.append(None)
    # مرحلة 2: علامة موجود أو غائب
    for i, ch in enumerate(guess_text):
        if feedback[i] is None:
            if ch in target_chars:
                feedback[i] = 'present'
                target_chars[target_chars.index(ch)] = None
            else:
                feedback[i] = 'absent'

    # حفظ كل LetterFeedback
    for pos, status in enumerate(feedback, start=1):
        LetterFeedback.objects.create(
            guess=guess,
            position=pos,
            letter=guess_text[pos-1],
            status=status
        )

    # إذا كان الحلّ كاملاً، أو انتهت المحاولات
    if all(s == 'correct' for s in feedback):
        puzzle.solved = True
        puzzle.save()
        return JsonResponse({'feedback': feedback, 'redirect': True})
    if attempt_number >= puzzle.max_attempts:
        return JsonResponse({'feedback': feedback, 'redirect': True})

    # خلاف ذلك، أرجع feedback فقط
    return JsonResponse({'feedback': feedback, 'redirect': False})



@login_required
def resultWordle(request, puzzle_id):
    # جلب الـ Puzzle الخاص بالمستخدم
    puzzle = get_object_or_404(Puzzle, id=puzzle_id, user=request.user)
    # عدّ عدد التخمينات التي أدخلها المستخدم
    used_attempts = Guess.objects.filter(puzzle=puzzle).count()
    # الكلمة الصحيحة (مثلاً الإنجليزية)
    correct_word = puzzle.word.eng_word.upper()
    # حالة الفوز: True إذا حلّ المستخدم
    solved = puzzle.solved

    context = {
        'correct_word': correct_word,
        'used_attempts': used_attempts,
        'solved': solved,
        'puzzle_id': puzzle.id,
    }
    return render(request, 'wordle/resultWordle.html', context)



@login_required
def resultHistoryWordle(request):
    puzzles = Puzzle.objects.filter(user=request.user).order_by('-played_at')
    history = []
    for p in puzzles:
        used_attempts = Guess.objects.filter(puzzle=p).count()
        history.append({
            'date'    : p.played_at.strftime('%Y-%m-%d %H:%M:%S'),
            'word'    : p.word.eng_word.upper(),
            'attempts': used_attempts,
            'won'     : p.solved,
        })
    return render(request, 'wordle/resultHistoryWordle.html', {
        'history': history
    })