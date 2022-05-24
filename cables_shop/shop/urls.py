from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('cables/', views.all_cables, name='all_cables'),
]
