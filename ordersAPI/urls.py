from django.urls import path
from . import views 

urlpatterns = [
    path('createOrder', views.create_order, name = 'create_order'),
    path('addKitchenOrder', views.AddKitchenOrder, name = 'AddKitchenOrder'),
    path('removeKitchenOrder', views.RemoveKitchenOrder, name = 'RemoveKitchenOrder'),
    path('getKitchenOrders', views.get_kitchen_orders, name= 'getKitchenOrders'),
    path('restockReport', views.restockReport, name = 'restock_report'),
    path('salesReport', views.salesReport, name = 'sales_report'),
    path('productUsageReport', views.product_Usage_Report, name = 'productUsageReport'),
    path('xreport', views.X_report, name = 'x_report'),
    path('zreport', views.Z_report, name = 'z_report'),
]