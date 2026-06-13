from django.contrib import admin

from django.contrib import admin
from .models import ToiletStatus

@admin.register(ToiletStatus)
class ToiletStatusAdmin(admin.ModelAdmin):
    # This shows the Toilet ID, Occupied Status, and Last Updated time in a clean list
    list_display = ('toilet_id', 'is_occupied', 'last_updated')
    # This adds a quick filter sidebar on the right side
    list_filter = ('is_occupied',)