
from django.urls import path
from . import views



urlpatterns=[
    path('',views.wordList, name='wordList'),
    path('wordAdd/',views.wordAdd, name='wordAdd'),
    path('wordDetails/<int:pk>/',views.wordDetails, name='wordDetails'),
    path('<int:pk>/', views.wordDelete, name='wordDelete'),
]
