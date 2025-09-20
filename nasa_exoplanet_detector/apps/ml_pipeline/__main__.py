from .model_trainer import train_all
import os

if __name__ == '__main__':
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sample = os.path.join(BASE_DIR, 'data', 'sample', 'kepler_sample.csv')
    print(train_all(sample if os.path.exists(sample) else None))
