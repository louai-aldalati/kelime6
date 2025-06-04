from django.urls import path
from . import views

urlpatterns=[
    path('',views.reportsList, name='reportsList'),
    path('dailyPerformance/',views.dailyPerformance, name='dailyPerformance'),
    path('difficultWords/',views.difficultWords, name='difficultWords'),
    path('quizSessions/',views.quizSessions, name='quizSessions'),
]