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
    with open(os.path.join(MODELS_DIR, f'{best}.pkl'), 'rb') as f:
        payload = pickle.load(f)
    return payload['model'], {'features': payload.get('features', REQUIRED_FEATURES), 'model_name': best}


def predict_single(model, features: dict, meta: dict):
    ordered = [float(features.get(k, 0)) for k in meta['features']]
    X = np.array(ordered).reshape(1, -1)
    probs = None
    probabilities_dict = {}
    
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X)[0]
        pred = model.classes_[probs.argmax()]
        conf = float(probs.max())
        # Create a dictionary mapping class names to probabilities
        for i, class_name in enumerate(model.classes_):
            probabilities_dict[str(class_name)] = float(probs[i])
    else:
        pred = model.predict(X)[0]
        conf = 1.0
        probabilities_dict[str(pred)] = 1.0
    
    return str(pred), conf, probabilities_dict
