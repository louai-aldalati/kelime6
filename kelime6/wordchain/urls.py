from django.urls import path
from . import views

urlpatterns=[
    path('',views.startWordchain, name='startWordchain'),
    path('playWordchain/',views.playWordchain, name='playWordchain'),
    path('resultWordchain/',views.resultWordchain, name='resultWordchain'),
]