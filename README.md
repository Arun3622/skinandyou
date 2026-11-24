# Skin & You

Skin & You is a Django application with a bundled web interface.

## Run locally

On Windows, the included `Start-Local.ps1` launcher expects a locally
provisioned Python environment at `.local/venv` and a PostgreSQL service with
local-only credentials under `%LOCALAPPDATA%\SkinAndYouLocal`. Those runtime
files and database records are intentionally not part of this repository.

Install the Python dependencies into that environment with:

```powershell
py -m venv .local\venv
.\.local\venv\Scripts\python.exe -m pip install -r requirements-local.txt
Copy-Item www\skin_and_you\skin_and_you\local_settings.py.example www\skin_and_you\skin_and_you\local_settings.py
```

After provisioning the local database and runtime secrets, start the app with:

```powershell
.\Start-Local.ps1
```

The local server listens on `http://127.0.0.1:8000/`.

## Configuration and data

The default Django settings require `DJANGO_SECRET_KEY` and accept database
settings through `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
Set `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` to comma-separated values
for the deployment; the defaults are restricted to local development.

Do not commit real patient/client data, database exports, uploaded media,
OAuth credentials, private keys, or environment files. Use synthetic data for
tests and demos. This repository intentionally excludes local backups,
credentials, generated data, and runtime databases. The app schema can still
contain fields such as phone numbers because those are part of the application
model; do not put real user values in source, fixtures, or public demo data.
Contact banners containing phone numbers or addresses and staff portraits are
also omitted. The bundled Font Awesome Pro files are not redistributed; the
licensed assets must be supplied locally if that icon pack is required.

`runserver` is for local development only. Configure production secrets,
database access, HTTPS, and deployment settings separately before deploying.
