from django.contrib import admin
from .models import *


class CableTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'name_plural', 'description', 'slug')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(CableType, CableTypeAdmin)
