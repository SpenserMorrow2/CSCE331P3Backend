from django.urls import path
from . import views

urlpatterns = [
    path('get-token/', views.get_token_for_manager, name='get_token_for_manager'),
    path('logout/', views.logout_user, name='logout_user'),
]
