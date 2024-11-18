from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # URL principale de l'application "home"
]

