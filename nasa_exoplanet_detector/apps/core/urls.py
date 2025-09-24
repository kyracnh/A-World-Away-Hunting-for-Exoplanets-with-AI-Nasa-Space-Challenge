from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload, name='upload'),
    path('predict/', views.predict, name='predict'),
    path('results/', views.results, name='results'),
    path('download-csv/', views.download_results_csv, name='download_csv'),
    path('health/', views.api_health, name='health'),
]
