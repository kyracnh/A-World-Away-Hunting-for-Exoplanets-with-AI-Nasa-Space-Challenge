from django.urls import path
from .views import predict_api, batch_predict_api, list_models

urlpatterns = [
    path('predict/', predict_api, name='api_predict'),
    path('batch/', batch_predict_api, name='api_batch'),
    path('models/', list_models, name='api_models'),
]
