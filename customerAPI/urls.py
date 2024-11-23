from django.urls import path
from . import views 

urlpatterns = [
    path('addCustomer', views.add_customer, name = 'add_customer'),
    path('login', views.login_customer, name = 'login_customer'),
    path('applyDiscounts', views.apply_discounts, name = 'apply_discounts'), 
    
]