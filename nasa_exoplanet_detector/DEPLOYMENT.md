# NASA Exoplanet Detector - Deployment Guide

## Quick Setup for New Machine

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd nasa_exoplanet_detector
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will automatically:
- Create virtual environment
- Install dependencies
- Run migrations
- Train models (if needed)
- Create admin user
- Start the server

### 3. Alternative Manual Setup

If setup.sh doesn't work:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Troubleshooting

### Model File Not Found Error
If you get "Model file not found" error:
1. Make sure trained models are committed to git
2. Run `python apps/ml_pipeline/model_trainer.py` to retrain models
3. Or run `./setup.sh` which includes model training

### Virtual Environment Issues
- Never commit `.venv` directory to git
- Always create new virtual environment on each machine
- Use `requirements.txt` for dependency management

### Database Issues
- `db.sqlite3` is not committed to git (intentionally)
- Run `python manage.py migrate` to create new database
- Default admin user: username=`admin`, password=`admin`

## Production Deployment

For production deployment, consider:
1. Use PostgreSQL instead of SQLite
2. Set `DEBUG = False` in settings
3. Configure proper static file serving
4. Use environment variables for secrets
5. Use proper web server (nginx + gunicorn)
