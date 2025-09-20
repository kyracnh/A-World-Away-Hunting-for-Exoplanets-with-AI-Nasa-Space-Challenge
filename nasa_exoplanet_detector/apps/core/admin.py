from django.contrib import admin
from .models import ExoplanetData, Prediction

@admin.register(ExoplanetData)
class ExoplanetDataAdmin(admin.ModelAdmin):
    list_display = ('name','orbital_period','transit_duration','planet_radius','stellar_temp','classification','created_at')

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('prediction','confidence','model_name','created_at')
