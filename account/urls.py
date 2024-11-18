from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.account, name='account'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('account/delete/', views.delete_account, name='delete_account'),
]
