from django.db import models
from django.conf import settings

# Create your models here.



class Puzzle(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word        = models.ForeignKey('wordadder.Word', on_delete=models.CASCADE)     # الكلمة الهدف
    word_length = models.PositiveSmallIntegerField()   # 4–7
    max_attempts   = models.PositiveSmallIntegerField()   # 4–7
    played_at   = models.DateTimeField(auto_now_add=True)  
    solved      = models.BooleanField(default=False)
    
    



class Guess(models.Model):
    puzzle         = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
    )
    guess_text     = models.CharField(max_length=255)                    # النص المدخل
    attempt_number = models.PositiveSmallIntegerField()                  # رقم المحاولة (1–6)




class LetterFeedback(models.Model):
    guess      = models.ForeignKey(
        Guess,
        on_delete=models.CASCADE,
    )
    position   = models.PositiveSmallIntegerField()                     # موقع الحرف (1–7)
    letter     = models.CharField(max_length=1)

    class FeedbackStatus(models.TextChoices):
        CORRECT = 'correct', 'Correct'
        PRESENT = 'present', 'Present'
        ABSENT  = 'absent',  'Absent'

    status     = models.CharField(
        max_length=7,
        choices=FeedbackStatus.choices
    )


