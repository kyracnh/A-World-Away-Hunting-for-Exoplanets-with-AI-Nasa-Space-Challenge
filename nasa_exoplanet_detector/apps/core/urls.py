from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload, name='upload'),
    path('predict/', views.predict, name='predict'),
    path('health/', views.api_health, name='health'),
]
