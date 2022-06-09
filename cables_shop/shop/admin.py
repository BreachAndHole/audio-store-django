from django.contrib import admin
from .models import *


# Products related
@admin.register(CableType)
class CableTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'name_plural', 'description', 'slug')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ('name', 'length_sm', 'price', 'units_in_stock')
    list_display_links = ('name',)
    list_editable = ('price', 'units_in_stock')
    list_filter = ('type',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CablePhoto)
class CablePhotoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cable', 'is_title', 'photo')
    list_display_links = ('cable',)
    list_filter = ('cable', 'is_title')


# Orders related
@admin.register(User)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'email', 'phone_number')
    list_display_links = ('last_name',)
    ordering = ('-id',)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'state', 'city')
    list_filter = ('customer',)
    ordering = ('customer', 'address')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status')
    list_filter = ('status', 'customer')


@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    list_filter = ('order', 'product')
