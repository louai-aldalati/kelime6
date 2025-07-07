from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import uuid
import logging
from django.core.files.base import ContentFile
from .models import WordChainGame,WordChainEntry
from wordadder.models import Word
from django.contrib import messages

# استيراد دوال التوليد من ملف gemini_api.py
from .utils.gemini_api import generate_story_gemini, generate_image_gemini



# Create your views here.

@login_required
def startWordchain(request):
    # جلب جميع الألعاب الخاصة بالمستخدم مرتّبة تنازلياً حسب وقت اللعب
    history = WordChainGame.objects.filter(user=request.user).order_by('-played_at')
    return render(request, 'wordchain/startWordchain.html', {
        'history': history,
    })




@login_required
def playWordchain(request):
    if request.GET.get('reset'):
        request.session.pop('current_game_id', None)
        return redirect('playWordchain')
    # 1. إذا كان طلب POST → إضافة كلمة جديدة إلى اللعبة الجارية
    if request.method == 'POST':
        game_id = request.session.get('current_game_id')
        game = get_object_or_404(WordChainGame, pk=game_id, user=request.user)

        eng_input = request.POST.get('eng_word', '').strip()
        try:
            next_word_obj = Word.objects.get(eng_word__iexact=eng_input , user=request.user)
        except Word.DoesNotExist:
            messages.error(request, "Bu İngilizce kelime mevcut değil.")
            return redirect('playWordchain')

        last_entry = game.wordchainentry_set.order_by('position').last()
        current_eng = last_entry.word.lower()
        if next_word_obj.eng_word[0].lower() != current_eng[-1]:
            messages.error(request, f"Kelime '{current_eng[-1].upper()}' harfi ile başlamalı.")
        else:
            WordChainEntry.objects.create(
                word_chain_game=game,
                word=next_word_obj.eng_word,
                position=last_entry.position + 1
            )
        return redirect('playWordchain')

    # 2. طلب GET → استرجاع اللعبة الجارية من الجلسة أو إنشاء واحدة جديدة
    game_id = request.session.get('current_game_id')
    if game_id:
        try:
            game = WordChainGame.objects.get(pk=game_id, user=request.user)
        except WordChainGame.DoesNotExist:
            game = None
    else:
        game = None

    if not game:
        # لم توجد لعبة جارية → أنشئ لعبة وكلمة أولى عشوائية
        game = WordChainGame.objects.create(user=request.user)
        first = Word.objects.filter(user=request.user).order_by('?').first()
        WordChainEntry.objects.create(
            word_chain_game=game,
            word=first.eng_word,
            position=1
        )
        # خزّن الـ game_id في الجلسة
        request.session['current_game_id'] = game.id

    # 3. اجهّز بيانات العرض
    entries = game.wordchainentry_set.order_by('position')
    current_eng = entries.last().word
    last_char = current_eng[-1].lower()
    candidates = Word.objects.filter(
        user=request.user,
        eng_word__istartswith=last_char
    ).order_by('eng_word')

    # بنية الإدخالات مع الترجمة
    entries_with_trans = []
    for e in entries:
        w = Word.objects.get(eng_word=e.word , user=request.user)
        entries_with_trans.append({'eng': e.word, 'tur': w.tur_word})

    return render(request, 'wordchain/playWordchain.html', {
        'entries': entries_with_trans,
        'current_word': current_eng,
        'candidates': candidates,
        'game_id': game.id,  # جاهز لو احتجت في القالب
    })


logger = logging.getLogger(__name__)


@login_required
def resultWordchain(request):
    # 1. استرجاع اللعبة الجارية
    game = get_object_or_404(
        WordChainGame,
        pk=request.session.get('current_game_id'),
        user=request.user
    )

    # 2. تجهيز prompt الخاص بالقصة
    entries = game.wordchainentry_set.order_by('position').values_list('word', flat=True)

    # نصّ التعليمات للنموذج: 
    # - استخدم الكلمات الإنجليزية كما هي، وبقية النص بالتركي.
    # - لا تقدم أي جملة تمهيدية أو رابط للعبة، ابدأ بسرد الحكاية مباشرةً.
    # - حافظ على القصة قصيرة وموجزة خاصةً إذا كان عدد الكلمات الإنجليزية قليل.
    prompt_text = (
        f"Aşağıdaki İngilizce kelimeleri hikâyede aynen kullanın ve geri kalan metni tamamen Türkçe yazın. "
        f"Hiçbir önsöz eklemeyin; doğrudan hikâyeyi başlatın. "
        f"Eğer İngilizce kelime sayısı azsa (örn. 3), hikâyeyi kısa tutun:\n\n"
    )
    for idx, w in enumerate(entries, 1):
        prompt_text += f"{idx}. {w}\n"

    # 3. توليد القصة باستخدام الدالة من gemini_api.py
    try:
        story_text = generate_story_gemini(prompt_text)
    except Exception as e:
        logger.error("خطأ أثناء توليد القصة من Gemini: %s", e, exc_info=True)
        messages.error(request, f"Hata (Gemini Text): {e}")
        return redirect('playWordchain')

    game.story = story_text
    
    '''
    # 4. إعداد prompt خاص بالصورة بالاعتماد على القصة المولّدة
    prompt_image = (
        "Bir dijital sanat eseri oluştur: Aşağıdaki hikayeyi anime tarzında, "
        "canlı renklerle ve ayrıntılı bir sahne olarak betimle.\n\n"
        f"Hikaye:\n{story_text}"
    )

    # 5. توليد الصورة باستخدام الدالة المحدثة
    try:
        img_bytes = generate_image_gemini(prompt_image)
    except Exception as e:
        logger.error("خطأ أثناء توليد الصورة من Gemini: %s", e, exc_info=True)
        messages.error(request, f"Resim oluşturulamadı; Hata: {e}")
        return redirect('playWordchain')

    filename = f"story_{game.id}_{uuid.uuid4().hex[:8]}.png"
    game.story_image.save(filename, ContentFile(img_bytes), save=False)
    '''
    
    game.save()

    # 6. مسح الجلسة والعودة إلى قالب النتائج
    del request.session['current_game_id']
    return render(request, 'wordchain/resultWordchain.html', {
        'story_text': game.story,
        #'story_image_url': game.story_image.url,
        'entries': entries,
    }) 