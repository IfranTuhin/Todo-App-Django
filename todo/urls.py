from django.urls import path
# pyrefly: ignore[missing-import]
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('add/', views.task_create, name = 'task_create'),
    path('delete/<int:task_id>/', views.task_delete, name = 'task_delete'),
    path('edit/<int:task_id>/', views.task_edit, name = 'task_edit'),
    path('toggle/<int:task_id>/', views.task_toggle, name = 'task_toggle'),
]                                                           