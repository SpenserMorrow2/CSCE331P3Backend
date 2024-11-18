from django.urls import path
from . import views 

urlpatterns = [
    path('names/', views.MenuItemNames, name = 'MenuItemNames'),
    path('items/', views.MenuItems, name = 'MenuItems'),
    path('item/<int:id>', views.MenuItemDetail, name = 'MenuItemDetail'),
    path('item/<int:id>/price', views.MenuItemPrice, name = 'MenuItemPrice'),
    path('addItem/', views.addMenuItem, name = "addMenuItem"), 
    path('removeItem/<int:removalid>', views.removeMenuItem, name = 'removeMenuItem'),

]