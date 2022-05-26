from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexPage.as_view(), name='home_page'),
    path('cables/', views.AllCablesPage.as_view(), name='all_cables_page'),
    path('cable/<slug:cable_slug>', views.CablePage.as_view(), name='cable_page'),
    path('cart/', views.cart, name='cart_page'),
]
