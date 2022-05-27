from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexPageView.as_view(), name='home_page'),
    path('cables/', views.AllCablesPageView.as_view(), name='all_cables_page'),
    path('cable/<slug:cable_slug>', views.CablePageView.as_view(), name='cable_page'),
    path('cart/', views.cart, name='cart_page'),
    path('checkout/', views.CheckoutPageView.as_view(), name='checkout_page'),
    path('update_item/', views.update_item),
]
