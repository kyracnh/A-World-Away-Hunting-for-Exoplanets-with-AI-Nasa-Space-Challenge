from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import csv
import pandas as pd
from datetime import datetime
from io import StringIO

from apps.ml_pipeline.predictor import load_best_model, predict_single
from apps.ml_pipeline.data_loader import COLUMNS_MAP, LABEL_MAP
from .models import Prediction, ExoplanetData


def dashboard(request):
    return render(request, 'core/dashboard.html', {})


def upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # Process the uploaded CSV file
            csv_file = request.FILES['file']
            
            # Read CSV content
            file_content = csv_file.read().decode('utf-8')
            csv_data = StringIO(file_content)
            
            # Read CSV with pandas, handle comments
            df = pd.read_csv(csv_data, comment='#')
            
            # Load ML model
            model, meta = load_best_model()
            
            predictions_created = 0
            errors = []
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract features based on column mapping
                    data = {}
                    
                    # Try to map columns - handle both direct column names and Kepler KOI format
                    if 'orbital_period' in df.columns:
                        data['orbital_period'] = float(row.get('orbital_period', 0))
                    elif 'koi_period' in df.columns:
                        data['orbital_period'] = float(row.get('koi_period', 0))
                    else:
                        data['orbital_period'] = float(row.iloc[0] if len(row) > 0 else 0)
                    
                    if 'transit_duration' in df.columns:
                        data['transit_duration'] = float(row.get('transit_duration', 0))
                    elif 'koi_duration' in df.columns:
                        data['transit_duration'] = float(row.get('koi_duration', 0))
                    else:
                        data['transit_duration'] = float(row.iloc[1] if len(row) > 1 else 0)
                    
                    if 'planet_radius' in df.columns:
                        data['planet_radius'] = float(row.get('planet_radius', 0))
                    elif 'koi_prad' in df.columns:
                        data['planet_radius'] = float(row.get('koi_prad', 0))
                    else:
                        data['planet_radius'] = float(row.iloc[2] if len(row) > 2 else 0)
                    
                    if 'stellar_temp' in df.columns:
                        data['stellar_temp'] = float(row.get('stellar_temp', 0) or 0)
                    elif 'koi_steff' in df.columns:
                        data['stellar_temp'] = float(row.get('koi_steff', 0) or 0)
                    else:
                        data['stellar_temp'] = float(row.iloc[3] if len(row) > 3 else 0)
                    
                    # Skip if essential data is missing
                    if data['orbital_period'] <= 0 or data['transit_duration'] <= 0 or data['planet_radius'] <= 0:
                        continue
                    
                    # Make prediction
                    pred, conf, probabilities = predict_single(model, data, meta)
                    
                    # Save prediction to database
                    Prediction.objects.create(
                        input_data=data,
                        prediction=pred,
                        confidence=conf,
                        probabilities=probabilities,
                        model_name=meta.get('model_name', 'Unknown')
                    )
                    
                    # Also save as ExoplanetData if we have a name/classification
                    if 'name' in row or 'kepoi_name' in row:
                        name = row.get('name') or row.get('kepoi_name', f'Object_{index}')
                        classification = pred  # Use our prediction as classification
                        
                        ExoplanetData.objects.create(
                            name=str(name)[:100],  # Limit to field max length
                            orbital_period=data['orbital_period'],
                            transit_duration=data['transit_duration'],
                            planet_radius=data['planet_radius'],
                            stellar_temp=data['stellar_temp'],
                            classification=classification
                        )
                    
                    predictions_created += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    continue
            
            message = f'Successfully processed {predictions_created} predictions.'
            if errors:
                message += f' {len(errors)} rows had errors.'
            
            return render(request, 'core/upload.html', {
                'message': message,
                'predictions_created': predictions_created,
                'errors': errors[:10]  # Show first 10 errors only
            })
            
        except Exception as e:
            return render(request, 'core/upload.html', {
                'message': f'Error processing file: {str(e)}',
                'error': True
            })
    
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
        pred, conf, probabilities = predict_single(model, data, meta)
        
        # Save prediction to database
        prediction_obj = Prediction.objects.create(
            input_data=data,
            prediction=pred,
            confidence=conf,
            probabilities=probabilities,
            model_name=meta.get('model_name', 'Unknown')
        )
        
        return render(request, 'core/predict.html', {
            'result': pred, 
            'confidence': conf, 
            'probabilities': probabilities,
            'data': data,
            'prediction_id': prediction_obj.id
        })
    return render(request, 'core/predict.html')


def results(request):
    """Display all prediction results"""
    predictions = Prediction.objects.all()[:100]  # Limit to last 100 results
    return render(request, 'core/results.html', {'predictions': predictions})


def download_results_csv(request):
    """Download all predictions as CSV"""
    predictions = Prediction.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="exoplanet_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    header = ['ID', 'Created At', 'Orbital Period', 'Transit Duration', 'Planet Radius', 'Stellar Temp',
              'Prediction', 'Confidence', 'Model Name']
    
    # Add probability columns for each class
    if predictions.exists() and predictions.first().probabilities:
        prob_classes = list(predictions.first().probabilities.keys())
        for class_name in prob_classes:
            header.append(f'Probability_{class_name.replace(" ", "_")}')
    
    writer.writerow(header)
    
    # Write data
    for pred in predictions:
        row = [
            pred.id,
            pred.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            pred.input_data.get('orbital_period', ''),
            pred.input_data.get('transit_duration', ''),
            pred.input_data.get('planet_radius', ''),
            pred.input_data.get('stellar_temp', ''),
            pred.prediction,
            pred.confidence,
            pred.model_name
        ]
        
        # Add probability values
        if pred.probabilities:
            for class_name in prob_classes:
                row.append(pred.probabilities.get(class_name, ''))
        
        writer.writerow(row)
    
    return response


@csrf_exempt
def api_health(request):
    return JsonResponse({'status': 'ok'})
