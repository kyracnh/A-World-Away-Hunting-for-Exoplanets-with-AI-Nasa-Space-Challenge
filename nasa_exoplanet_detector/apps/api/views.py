from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from apps.ml_pipeline.predictor import load_best_model, predict_single, list_available_models
from .serializers import PredictInputSerializer

@csrf_exempt
def predict_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        serializer = PredictInputSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        model, meta = load_best_model()
        pred, conf = predict_single(model, serializer.validated_data, meta)
        return JsonResponse({'prediction': pred, 'confidence': conf})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def batch_predict_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        items = json.loads(request.body.decode('utf-8'))
        model, meta = load_best_model()
        results = []
        for row in items:
            serializer = PredictInputSerializer(data=row)
            serializer.is_valid(raise_exception=True)
            pred, conf = predict_single(model, serializer.validated_data, meta)
            results.append({'prediction': pred, 'confidence': conf})
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def list_models(request):
    return JsonResponse({'models': list_available_models()})
