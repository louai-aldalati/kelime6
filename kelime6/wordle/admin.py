from django.contrib import admin
from .models import Puzzle,Guess,LetterFeedback
# Register your models here.

admin.site.register(Puzzle)
admin.site.register(Guess)
admin.site.register(LetterFeedback)
