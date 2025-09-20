import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

from .data_loader import ensure_datasets, load_and_prepare

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'trained_models')

FEATURES = ['orbital_period', 'transit_duration', 'planet_radius', 'stellar_temp']
TARGET = 'label'


def train_all(offline_sample: str | None = None) -> dict:
    os.makedirs(MODELS_DIR, exist_ok=True)
    paths = ensure_datasets(offline_sample)
    df = load_and_prepare(paths)

    # Fill missing stellar_temp with median
    if 'stellar_temp' in df.columns:
        df['stellar_temp'] = df['stellar_temp'].fillna(df['stellar_temp'].median())
    else:
        df['stellar_temp'] = 0

    X = df[FEATURES]
    y = df[TARGET]

    # Choose split strategy robustly for small datasets
    test_size = 0.2 if len(y) >= 100 else 0.33
    stratify = y if (y.nunique() >= 2 and y.value_counts().min() >= 2) else None
    if stratify is None and y.nunique() < 2:
        raise ValueError('Dataset must contain at least two classes to train a classifier.')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=stratify
    )

    results = {}

    configs = {
        'RandomForest': Pipeline([
            ('clf', RandomForestClassifier(n_estimators=300, random_state=42))
        ]),
        'SVM': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', SVC(kernel='rbf', probability=True, C=3.0, gamma='scale', random_state=42))
        ]),
        'NeuralNet': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=42))
        ]),
    }

    for name, model in configs.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        results[name] = {'accuracy': acc}
        with open(os.path.join(MODELS_DIR, f'{name}.pkl'), 'wb') as f:
            pickle.dump({'model': model, 'features': FEATURES}, f)

    # Choose best
    best = max(results.items(), key=lambda kv: kv[1]['accuracy'])[0]
    with open(os.path.join(MODELS_DIR, 'BEST.txt'), 'w') as f:
        f.write(best)

    return results

if __name__ == '__main__':
    # Allow local run
    sample = os.path.join(BASE_DIR, 'data', 'sample', 'kepler_sample.csv')
    if not os.path.exists(sample):
        sample = None
    print(train_all(sample))
