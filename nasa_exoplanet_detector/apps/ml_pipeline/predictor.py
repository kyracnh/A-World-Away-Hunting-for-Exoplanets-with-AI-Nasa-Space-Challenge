import os
import pickle
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'trained_models')

REQUIRED_FEATURES = ['orbital_period', 'transit_duration', 'planet_radius', 'stellar_temp']
CLASS_ORDER = ['Confirmed', 'Candidate', 'False Positive']


def list_available_models():
    models = []
    for fname in os.listdir(MODELS_DIR):
        if fname.endswith('.pkl'):
            models.append(fname.replace('.pkl', ''))
    return models


def load_best_model():
    best_path = os.path.join(MODELS_DIR, 'BEST.txt')
    if not os.path.exists(best_path):
        # fallback: any model
        models = list_available_models()
        if not models:
            raise FileNotFoundError('No trained models found. Run setup.sh to train models.')
        best = models[0]
    else:
        with open(best_path, 'r') as f:
            best = f.read().strip()
    
    model_path = os.path.join(MODELS_DIR, f'{best}.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f'Model file {model_path} not found.')
    
    try:
        with open(model_path, 'rb') as f:
            payload = pickle.load(f)
        
        if 'model' not in payload:
            raise ValueError(f'Invalid model file structure in {model_path}')
            
        return payload['model'], {
            'features': payload.get('features', REQUIRED_FEATURES), 
            'model_name': best
        }
    except Exception as e:
        raise RuntimeError(f'Error loading model from {model_path}: {str(e)}')


def predict_single(model, features: dict, meta: dict):
    ordered = [float(features.get(k, 0)) for k in meta['features']]
    X = np.array(ordered).reshape(1, -1)
    probs = None
    probabilities_dict = {}
    
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X)[0]
        # Handle both Pipeline and direct model classes
        if hasattr(model, 'classes_'):
            classes = model.classes_
        elif hasattr(model, '_final_estimator') and hasattr(model._final_estimator, 'classes_'):
            classes = model._final_estimator.classes_
        else:
            # Fallback to default class order
            classes = np.array(CLASS_ORDER)
        
        pred_idx = int(np.argmax(probs))
        pred = str(classes[pred_idx])
        conf = float(probs.max())
        
        # Create a dictionary mapping class names to probabilities
        for i, class_name in enumerate(classes):
            probabilities_dict[str(class_name)] = float(probs[i])
    else:
        pred = str(model.predict(X)[0])
        conf = 1.0
        probabilities_dict[str(pred)] = 1.0
    
    return str(pred), conf, probabilities_dict
