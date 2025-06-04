from django.db import models
from django.conf import settings
# Create your models here.

class Quiz(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    taken_date = models.DateField(
        null=True,
        blank=True
    )


    def __str__(self):
        return f"Quiz {self.id} by {self.user.username} at {self.taken_date}"


class QuizItem(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
    )
    word = models.ForeignKey(
        'wordadder.Word', 
        on_delete=models.CASCADE,
    )
    correct = models.BooleanField()


    def __str__(self):
        return f"QuizItem {self.id}: Quiz {self.quiz.id} – Word {self.word.id} – Correct: {self.correct}"
