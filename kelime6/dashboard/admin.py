from django.contrib import admin
from .models import UserWordProgress,DailyPerformance
# Register your models here.
admin.site.register(UserWordProgress)
admin.site.register(DailyPerformance)