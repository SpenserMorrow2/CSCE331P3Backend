from django.urls import path
from . import views 

urlpatterns = [
    path('active/', views.getActiveEmployees, name = 'getactiveEmployees'),
    path('activeManagerID/', views.getActiveManagerID, name = 'getActiveManagerID'),
    path('<int:employeeid>', views.getEmployeeInfo, name='getEmployeeInfo'),
    path('addEmployee', views.addEmployee, name='addEmployee'),
    path('changeStatus/<int:employeeid>', views.fireEmployee, name='fireEmployee'),
    path('getActiveNonManagers', views.getAllActiveEmployeesNonManager, name='getAllActiveEmployeesNonManager'),
    path('getInactiveEmployees', views.getAllInActiveEmployees, name='getAllInActiveEmployees'),
    path('promoteEmployees', views.PromoteEmployees, name='PromoteEmployees')
]