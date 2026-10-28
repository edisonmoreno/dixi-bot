# Miniconda
Descarga: https://www.anaconda.com/download/success?reg=skipped-miniconda

**Instalación:**

- Marcar "Clear package cache upon completion"

**Comandos:**
| comando | descripción |
|--|--|
|`conda --version`|versión|
|`conda create --prefix ./env python=3.11 -y`|Crear ambiente en proyecto|
|`conda activate ./env`|Activar ambiente en proyecto|
|`conda env create -f environment.yml`|Crea ambiente en proyecto basado .yml|
|`conda activate dixi-bot`|Activar ambiente en proyecto|
|`conda deactivate`|Desactivar el ambiente|
|`conda env update -f environment.yml --prune`|Actualizar libs|

# Requisitos
- con conda: 
    - `conda env create -f environment.yml`
    - `conda activate dixi-bot`
    - `conda env update -f environment.yml --prune`
- sin conda: `pip install -r requirements.txt`

## Front
- `pip install streamlit`
    - run: `streamlit run ui/app.py --server.sslCertFile=ui/certs/dixibot-https-cert.pem --server.sslKeyFile=ui/certs/dixibot-https-key.pem`
    - https://app.dixibot.local:8501 o https://admin.dixibot.local:8501
- `pip install streamlit[auth]` > Autenticación

