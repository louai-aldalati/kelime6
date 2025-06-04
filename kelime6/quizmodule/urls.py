from django.urls import path
from . import views

urlpatterns=[
    path('',views.quizDashboard, name='quizDashboard'),
    path('quizQuestion/',views.quizQuestion, name='quizQuestion'),
    path('quizSummary/',views.quizSummary, name='quizSummary'),
    path('quizHistory/',views.quizHistory, name='quizHistory'),
]