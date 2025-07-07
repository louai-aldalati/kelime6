from django.urls import path
from . import views

urlpatterns=[
    path('',views.startWordle, name='startWordle'),
    path('boardWordle/<int:puzzle_id>/',views.boardWordle, name='boardWordle'),
    # هذا المسار للتخمينات:
    path('boardWordle/<int:puzzle_id>/guess/', views.boardWordleGuess, name='boardWordleGuess'),
    path('resultWordle/<int:puzzle_id>/',views.resultWordle, name='resultWordle'),
    path('resultHistoryWordle/',views.resultHistoryWordle, name='resultHistoryWordle'),
]
#