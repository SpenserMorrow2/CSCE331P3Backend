from django.urls import path
from . import views 
#from P3BackEnd import settings
#from django.conf.urls.static import static

urlpatterns = [
    path('names/', views.MenuItemNames, name = 'MenuItemNames'),
    path('items/', views.MenuItems, name = 'MenuItems'),
    path('item/<int:id>', views.MenuItemDetail, name = 'MenuItemDetail'),
    path('item/<int:id>/price', views.MenuItemPrice, name = 'MenuItemPrice'),
    path('addItem', views.addMenuItem, name = "addMenuItem"), #no slash now
    path('removeItem/<int:removalid>', views.removeMenuItem, name = 'removeMenuItem'),
    path('changeSmallPrice/<int:itemid>', views.changeSmallPrice, name ='changeSmallPrice'),
    path('changeMediumPrice/<int:itemid>', views.changeMediumPrice, name ='changeMediumPrice'),
    path('changeLargePrice/<int:itemid>', views.changeLargePrice, name ='changeLargePrice'),
    path('menuItemPicture/<int:itemID>', views.MenuItemPicture, name='MenuItemPicture'),
    path('uploadImage/<int:itemID>', views.UploadItemPicture, name='UploadItemPicture'),
    path('deleteImage/<int:itemID>', views.DeleteItemImage, name='DeleteItemImage')


]
