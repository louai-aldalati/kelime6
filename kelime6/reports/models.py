from django.db import models
from django.conf import settings
# Create your models here.

# أنواع التقارير المتاحة
REPORT_TYPE_CHOICES = [
    ('daily', 'Daily Performance Report'),
    ('difficult', 'Difficult Words Report'),
    ('quiz', 'Quiz Sessions Report'),
]


class Report(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        default='daily',  # يمكنك اختيار القيمة الافتراضية
        )

    generated_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='reports/%Y/%m/%d')

    def __str__(self):
        return f"Report {self.id} for {self.user.username} on {self.generated_at}"
