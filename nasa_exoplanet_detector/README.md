# NASA Exoplanet AI Detector

One-command setup Django app with ML models to classify exoplanet candidates using NASA Kepler KOI data.

## Quickstart

Run the setup script (creates venv, installs deps, downloads data, trains 3 models, runs server):

```bash
./setup.sh
```

Then open http://127.0.0.1:8000/

## Structure
- apps/core: Web UI
- apps/api: REST endpoints
- apps/ml_pipeline: Data loader, trainer, predictor
- data/: datasets (downloaded automatically)
- trained_models/: saved models

## Offline sample
If dataset download fails, a small sample CSV in `data/sample/kepler_sample.csv` will be used.
