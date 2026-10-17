from django.contrib import admin
# pyrefly: ignore[missing-import]
from .models import TaskModel

# Register your models here.
@admin.register(TaskModel)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'complated', 'created_at']
    list_filter = ['complated', 'updated_at']
    search_fields = ['title', 'description']
    ordering = ['created_at']

    
