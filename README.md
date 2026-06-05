# AIMS Doctor Entry

React + Django starter for doctor-entered clinical consultation data. Doctors start with `file_name`, fill the form sections from the ER diagram, submit JSON to Django, and Django stores the data in relational tables with an Excel export containing JSON payloads.

## Project Layout

- `frontend/` - React + Vite doctor data-entry UI.
- `backend/` - Django API, PostgreSQL-ready models, JSON and Excel export endpoints.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

By default Django uses SQLite for local development if `DATABASE_URL` is not set. For PostgreSQL, set this in `backend/.env`:

```env
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DATABASE
```

## Frontend Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend expects the backend at `http://localhost:8000/api`. Change `VITE_API_BASE_URL` in `frontend/.env` if needed.

## API Endpoints

- `GET /api/health/`
- `GET /api/schema/`
- `GET /api/consultations/`
- `POST /api/consultations/`
- `GET /api/consultations/<id>/json/`
- `GET /api/consultations/<id>/excel/`
- `GET /api/export/excel/`
- `GET /api/export/excel/save-to-downloads/` - local development only.

## Recommended Free Deployment

Use:

- Frontend: Vercel.
- Backend: Render free web service.
- Database: Neon free Postgres.

Render's free web service can sleep after inactivity, so the first request after a quiet period may be slow. Render free Postgres expires after 30 days, so Neon is a better free database choice for this app.

### 1. Create Neon Postgres

1. Create a Neon project.
2. Copy the pooled or standard Postgres connection string.
3. Keep it ready as `DATABASE_URL`.

### 2. Deploy Django Backend On Render

Create a new Render web service from this repo and use `backend/` as the root directory.

Render settings:

```text
Runtime: Python
Build command: ./build.sh
Start command: gunicorn aims_backend.wsgi:application
Plan: Free
```

Backend environment variables:

```env
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=your-render-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
DATABASE_URL=postgres://...
DATABASE_SSL_REQUIRE=True
```

After deploy, test:

```text
https://your-render-backend.onrender.com/api/health/
```

### 3. Deploy React Frontend On Vercel

Create a new Vercel project from this repo and use `frontend/` as the root directory.

Vercel settings:

```text
Framework preset: Vite
Build command: npm run build
Output directory: dist
```

Frontend environment variable:

```env
VITE_API_BASE_URL=https://your-render-backend.onrender.com/api
```

After deploy, update Render's `CORS_ALLOWED_ORIGINS` with the final Vercel URL and redeploy/restart the backend.

### Production Export Behavior

Local development saves Excel directly to your Windows Downloads folder because the Codex in-app browser does not handle downloads reliably.

In production, Excel export uses the normal browser download endpoint:

```text
/api/export/excel/
```
