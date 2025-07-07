from django.conf import settings
from django.db import models

# Create your models here.

class Word(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    eng_word = models.CharField(max_length=255)
    tur_word = models.CharField(max_length=255)
    picture = models.ImageField( upload_to='pictures/%Y/%m/%d',blank=True, null=True)
    voice = models.FileField(upload_to='voices/%Y/%m/%d',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.eng_word


class WordSample(models.Model):
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
    )
    samples = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.word_id.eng_word}: {self.samples[:50]}..."
