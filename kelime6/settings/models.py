from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.



class Setting(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    quiz_size = models.PositiveIntegerField(
       default=10,
       validators=[MinValueValidator(1), MaxValueValidator(50)]
    )


    def __str__(self):
        return f"Setting for {self.user.username}: quiz_size={self.quiz_size}"
