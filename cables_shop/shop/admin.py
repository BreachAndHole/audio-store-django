from django.contrib import admin
from .models import *


class CableTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'name_plural', 'description', 'slug')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class CableAdmin(admin.ModelAdmin):
    list_display = ('name', 'length_m', 'price', 'units_in_stock')
    list_display_links = ('name',)
    list_editable = ('price', 'units_in_stock')
    list_filter = ('type',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(CableType, CableTypeAdmin)
admin.site.register(Cable, CableAdmin)
