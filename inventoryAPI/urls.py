from django.urls import path
from . import views 

urlpatterns = [
    path('items/', views.getInventoryItems, name = 'getInventoryItems'),
    path('names/', views.getInventoryNames, name = 'getInventoryNames'),
    path('details/<int:rawitemid>', views.getInventoryDetails, name = 'getInventoryDetails'),
    path('nextInventoryID/', views.getNextRawID, name = 'getNextRawID'),
    path('nextJunctionID/', views.getNextJunctionID, name = 'getNextJunctionID'),
    path('rawItemsForMenuItem/<int:itemid>', views.getRawInventoryForMenuItem, name = 'getRawInventoryForMenuItem'),
    path('addItem', views.addInventoryItem, name = 'addInventoryItem'),
    path('removeInventory/<int:removalid>', views.removeInventoryItem, name = 'removeInventoryItem'),
    path('changeInventoryMin/<int:rawItemID>/<int:new_Min>', views.ChangeInventoryMin, name = 'ChangeInventoryMin'),
    path('restockInventoryItem/<int:rawItemID>/<int:quant>', views.RestockInventoryItem, name = 'RestockInventoryItem'),
    path('restockInventory', views.RestockInventory, name = 'RestockInventory'),
    path('changeName/<int:rawitemid>', views.changeInventoryName, name = 'changeInventoryName'),
    path('createJunctionEntry', views.createJunctionEntry, name='createJunctionEntry'),
    path('deleteJunctionEntry', views.deleteJunctionEntry, name='deleteJunctionEntry'),
    
]