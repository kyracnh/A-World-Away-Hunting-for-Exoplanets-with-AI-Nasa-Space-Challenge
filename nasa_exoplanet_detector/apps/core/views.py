from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from apps.ml_pipeline.predictor import load_best_model, predict_single


def dashboard(request):
    return render(request, 'core/dashboard.html', {})


def upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # For brevity, just return success; full parsing done in ML pipeline
        return render(request, 'core/upload.html', {'message': 'File received. Processing will run in background.'})
    return render(request, 'core/upload.html')


def predict(request):
    if request.method == 'POST':
        data = {
            'orbital_period': float(request.POST.get('orbital_period')),
            'transit_duration': float(request.POST.get('transit_duration')),
            'planet_radius': float(request.POST.get('planet_radius')),
            'stellar_temp': float(request.POST.get('stellar_temp', 0) or 0),
        }
        model, meta = load_best_model()
        pred, conf = predict_single(model, data, meta)
        return render(request, 'core/predict.html', {'result': pred, 'confidence': conf, 'data': data})
    return render(request, 'core/predict.html')


@csrf_exempt
def api_health(request):
    return JsonResponse({'status': 'ok'})
