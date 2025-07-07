from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

# Create your models here.

class UserWordProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    word = models.ForeignKey(
        'wordadder.Word',
        on_delete=models.CASCADE,
    )
    repetition_count = models.IntegerField( ) #from 0 to 6
    last_review = models.DateField(null=True, blank=True )
    next_review = models.DateField( )

    def __str__(self):
        return self.word.eng_word


class DailyPerformance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    date         = models.DateField()              # تاريخ الأداء
    correct      = models.PositiveIntegerField()   # عدد الإجابات الصحيحة في ذلك اليوم
    incorrect    = models.PositiveIntegerField()   # عدد الإجابات الخاطئة




