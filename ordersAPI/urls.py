from django.urls import path
from . import views 

urlpatterns = [
    path('createOrder', views.create_order, name = 'create_order'),
    path('removeKitchenOrder/<int:orderID>', views.RemoveKitchenOrder, name = 'RemoveKitchenOrder'),
    path('getKitchenOrders', views.get_kitchen_orders, name= 'getKitchenOrders'),
    path('restockReport', views.restockReport, name = 'restock_report'),
    path('salesReport/<str:start_d>/<str:end_d>', views.salesReport, name = 'sales_report'),
    path('productUsageReport/<str:start_date>/<str:end_date>', views.product_Usage_Report, name = 'productUsageReport'),
    path('xreport', views.X_report, name = 'x_report'),
    path('zreport', views.Z_report, name = 'z_report'),
    path('recentOrders', views.getRecentOrders, name = 'recentOrders'),
    path('expandRecentOrders', views.expandRecentOrders, name = 'expandRecent'),
    path('refund/<int:orderid>', views.refundOrder, name='refundOrder'),
    path('excessReport', views.excess_report, name= 'excess_report')
]