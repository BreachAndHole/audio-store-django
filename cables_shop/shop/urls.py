from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home_page'),
    path('cables/', views.all_cables, name='all_cables_page'),
    path('cable/<slug:cable_slug>', views.cable_page, name='cable_page'),
]
