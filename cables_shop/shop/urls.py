from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexPageView.as_view(), name='home_page'),
    path('cables/', views.AllCablesPageView.as_view(), name='all_cables_page'),
    path('cable/<slug:cable_slug>', views.CablePageView.as_view(), name='cable_page'),
    path('user/registration/', views.user_registration, name='user_registration_page'),
    path('user/login/', views.user_login, name='user_login_page'),
    path('user/logout/', views.user_logout, name='user_logout_page'),
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile_page'),
    path('cart/', views.CartPageView.as_view(), name='cart_page'),
    path('cart/checkout/', views.checkout, name='checkout_page'),
    path('updateCart/', views.update_cart, name='update_cart_page'),
    path('user/order/<int:order_pk>', views.order_information, name='order_info_page'),
    path('about/', views.AboutPageView.as_view(), name='about_page'),
]
