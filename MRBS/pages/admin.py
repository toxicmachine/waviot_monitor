from django.contrib import admin
from .models import ChangeHistory
# Register your models here.

@admin.register(ChangeHistory)
class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ('version', 'description')