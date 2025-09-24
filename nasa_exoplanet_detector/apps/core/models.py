from django.db import models

class ExoplanetData(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    orbital_period = models.FloatField()
    transit_duration = models.FloatField()
    planet_radius = models.FloatField()
    stellar_temp = models.FloatField(blank=True, null=True)
    classification = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

class Prediction(models.Model):
    input_data = models.JSONField()
    prediction = models.CharField(max_length=20)
    confidence = models.FloatField()
    probabilities = models.JSONField(blank=True, null=True)  # Store all class probabilities
    model_name = models.CharField(max_length=50, default='RandomForest')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
