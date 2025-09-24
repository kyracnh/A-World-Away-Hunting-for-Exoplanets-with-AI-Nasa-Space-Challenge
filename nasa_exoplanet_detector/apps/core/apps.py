from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    
    def ready(self):
        # Import here to avoid circular imports
        from .models import Prediction, ExoplanetData
        
        @receiver(post_migrate, sender=self)
        def clear_data_on_startup(sender, **kwargs):
            """Clear all prediction data when Django starts"""
            try:
                Prediction.objects.all().delete()
                ExoplanetData.objects.all().delete()
                print("🧹 Automatically cleared all prediction results on startup!")
            except Exception as e:
                print(f"⚠️  Could not auto-clear results: {e}")
