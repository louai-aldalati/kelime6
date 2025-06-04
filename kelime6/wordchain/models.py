from django.db import models
from django.conf import settings
# Create your models here.


class WordChainGame(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    played_at = models.DateTimeField(auto_now_add=True)
    story = models.TextField( blank=True, null=True)
    story_image = models.ImageField( upload_to='wordchain_pictures/%Y/%m/%d', blank=True, null=True)


class WordChainEntry(models.Model):
    word_chain_game = models.ForeignKey(
        WordChainGame, 
        on_delete=models.CASCADE,
    )
    word = models.CharField(max_length=255,)
    position = models.SmallIntegerField()


