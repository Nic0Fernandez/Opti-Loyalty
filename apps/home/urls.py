from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get_home_data/', views.get_home_data, name='get_home_data'),
]