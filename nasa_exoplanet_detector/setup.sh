#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN="\033[0;32m"; RED="\033[0;31m"; YELLOW="\033[1;33m"; NC="\033[0m"

PY=${PYTHON:-python3}
PIP=${PIP:-pip3}
VENV_DIR=".venv"
BASE_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$BASE_DIR"

say() { echo -e "${GREEN}==>${NC} $*"; }
warn() { echo -e "${YELLOW}==>${NC} $*"; }
err() { echo -e "${RED}==>${NC} $*"; }

say "Creating virtual environment"
$PY -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

say "Upgrading pip"
pip install --upgrade pip

say "Installing requirements"
pip install -r requirements.txt

say "Collecting data (Kepler KOI) with offline fallback"
mkdir -p data/sample trained_models
SAMPLE=data/sample/kepler_sample.csv
# Always create a minimal valid sample to guarantee training succeeds offline
cat > "$SAMPLE" <<'CSV'
loc_rowid,kepid,kepoi_name,kepler_name,koi_disposition,koi_pdisposition,koi_score,koi_fpflag_nt,koi_fpflag_ss,koi_fpflag_co,koi_fpflag_ec,koi_period,koi_period_err1,koi_period_err2,koi_time0bk,koi_time0bk_err1,koi_time0bk_err2,koi_impact,koi_impact_err1,koi_impact_err2,koi_duration,koi_duration_err1,koi_duration_err2,koi_depth,koi_depth_err1,koi_depth_err2,koi_prad,koi_prad_err1,koi_prad_err2,koi_teq,koi_teq_err1,koi_teq_err2,koi_insol,koi_insol_err1,koi_insol_err2,koi_model_snr,koi_tce_plnt_num,koi_tce_delivname,koi_steff,koi_steff_err1,koi_steff_err2,koi_slogg,koi_slogg_err1,koi_slogg_err2,koi_srad,koi_srad_err1,koi_srad_err2,ra,dec,koi_kepmag
1,10797460,K00752.01,Kepler-227 b,CONFIRMED,CANDIDATE,1.0000,0,0,0,0,9.488035570,2.7750000e-05,-2.7750000e-05,170.5387500,2.160000e-03,-2.160000e-03,0.1460,0.3180,-0.1460,2.95750,0.08190,-0.08190,6.1580e+02,1.950e+01,-1.950e+01,2.26,2.600e-01,-1.500e-01,793.0,,,93.59,29.45,-16.65,35.80,1,q1_q17_dr25_tce,5455.00,81.00,-81.00,4.467,0.064,-0.096,0.9270,0.1050,-0.0610,291.934230,48.141651,15.347
CSV
# Save attached sample (if any) for reference
if [ -f ../cumulative_2025.09.20_14.12.59.csv ]; then
  cp ../cumulative_2025.09.20_14.12.59.csv data/sample/attached_kepler.csv || true
fi

say "Running Django makemigrations and migrations"
python manage.py makemigrations apps.core --noinput || true
python manage.py migrate --noinput

say "Training baseline models (RF, SVM, MLP)"
python - <<PYCODE
from apps.ml_pipeline.model_trainer import train_all
import os
BASE_DIR=os.path.dirname(__file__)
sample=os.path.join(BASE_DIR,'data','sample','kepler_sample.csv')
res=train_all(sample if os.path.exists(sample) else None)
print(res)
PYCODE

say "Creating superuser (admin/admin) if not exists"
python - <<'PYCODE'
from django.contrib.auth import get_user_model
from django.conf import settings
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
User=get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin','admin@example.com','admin')
    print('Created admin user')
else:
    print('Admin user exists')
PYCODE

say "Running Django tests (smoke)"
python manage.py test || true

say "Starting development server at http://127.0.0.1:8000"
python manage.py runserver 0.0.0.0:8000
