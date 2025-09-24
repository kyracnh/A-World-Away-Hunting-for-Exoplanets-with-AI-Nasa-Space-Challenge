from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from apps.ml_pipeline.predictor import load_best_model, predict_single, list_available_models
from .serializers import PredictInputSerializer
from apps.core.models import Prediction

@csrf_exempt
def predict_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        serializer = PredictInputSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        model, meta = load_best_model()
        pred, conf, probabilities = predict_single(model, serializer.validated_data, meta)
        
        # Save prediction to database
        prediction_obj = Prediction.objects.create(
            input_data=serializer.validated_data,
            prediction=pred,
            confidence=conf,
            probabilities=probabilities,
            model_name=meta.get('model_name', 'Unknown')
        )
        
        return JsonResponse({
            'prediction': pred, 
            'confidence': conf,
            'probabilities': probabilities,
            'prediction_id': prediction_obj.id
        })
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
        prediction_ids = []
        
        for row in items:
            serializer = PredictInputSerializer(data=row)
            serializer.is_valid(raise_exception=True)
            pred, conf, probabilities = predict_single(model, serializer.validated_data, meta)
            
            # Save prediction to database
            prediction_obj = Prediction.objects.create(
                input_data=serializer.validated_data,
                prediction=pred,
                confidence=conf,
                probabilities=probabilities,
                model_name=meta.get('model_name', 'Unknown')
            )
            
            results.append({
                'prediction': pred, 
                'confidence': conf,
                'probabilities': probabilities,
                'prediction_id': prediction_obj.id
            })
            prediction_ids.append(prediction_obj.id)
            
        return JsonResponse({
            'results': results,
            'prediction_ids': prediction_ids,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def list_models(request):
    return JsonResponse({'models': list_available_models()})
