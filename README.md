# AWS Route 53 Clone — Scaler SDE Fullstack Assignment

🔗 **[Live Demo →](https://route53-clone-frontend-production.up.railway.app)**  
📦 **[GitHub Repository →](https://github.com/khyatiyadav06/AWS-route53-clone)**

A production-style full-stack recreation of the **AWS Route 53 management-console experience**. This project does not implement real DNS resolution or AWS infrastructure; it reproduces the requested console workflows, navigation, forms, tables, search, pagination, notifications and CRUD operations with SQLite persistence.

## Features

- Next.js 14 App Router + TypeScript
- FastAPI + Pydantic + SQLAlchemy REST API
- SQLite persistence with configurable database path
- Mock authentication with database-backed, expiring bearer sessions
- Next.js middleware route protection
- Hosted Zone complete CRUD
- DNS Record complete CRUD
- Required record types: A, AAAA, CNAME, TXT, MX, NS, PTR, SRV, CAA
- Server-side search and pagination
- Record-specific validation for supported DNS types
- AWS-console-inspired dark top bar, Route 53 sidebar, breadcrumbs and action menus
- Create/edit/delete confirmation modals
- Loading, empty, error and success states
- Responsive desktop/tablet layout
- Dashboard, Traffic Policies, Health Checks, Resolver and Profiles placeholder pages
- Seeded fictional demo environment
- Health endpoint
- Pytest/TestClient backend coverage
- Docker Compose local deployment
- Railway/Render backend deployment configuration
- Vercel/Render frontend Docker deployment support

## Architecture

```text
Browser
  |
  | Next.js / React / TypeScript
  | Bearer session token
  v
Next.js Frontend --------------------+
                                     |
                                     | REST / JSON
                                     v
                              FastAPI Backend
                               |     |     |
                               |     |     +-- Authentication/session dependency
                               |     +-------- Pydantic validation
                               +-------------- SQLAlchemy
                                      |
                                      v
                              SQLite persistent storage
```

Authentication is intentionally mocked for the assignment. The backend creates a random session token after successful demo login, stores it in SQLite with an expiry, and every protected API endpoint resolves the user through `get_current_user`.

## Folder structure

```text
route53-clone/
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── dashboard/
│   │   ├── hosted-zones/
│   │   │   └── [zoneId]/
│   │   ├── traffic-policies/
│   │   ├── health-checks/
│   │   ├── resolver/
│   │   └── profiles/
│   ├── components/
│   │   ├── layout/
│   │   ├── navigation/
│   │   ├── tables/
│   │   └── ui/
│   ├── lib/api.ts
│   ├── middleware.ts
│   ├── Dockerfile
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── tests.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── railway.toml
├── render.yaml
└── README.md
```

## Database schema

### users

| Column | Type |
|---|---|
| id | INTEGER PK |
| email | TEXT UNIQUE |
| name | TEXT |

### sessions

| Column | Type |
|---|---|
| id | INTEGER PK |
| token | TEXT UNIQUE |
| user_id | INTEGER FK |
| created_at | DATETIME |
| expires_at | DATETIME |

### hosted_zones

| Column | Type |
|---|---|
| id | INTEGER PK |
| name | TEXT |
| zone_id | TEXT UNIQUE |
| description | TEXT |
| zone_type | TEXT |
| created_at | DATETIME |

### dns_records

| Column | Type |
|---|---|
| id | INTEGER PK |
| hosted_zone_id | INTEGER FK |
| name | TEXT |
| type | TEXT |
| ttl | INTEGER |
| value | TEXT |
| routing_policy | TEXT |
| created_at | DATETIME |
| updated_at | DATETIME |

`dns_records.hosted_zone_id` references `hosted_zones.id` with cascade deletion.

## API overview

### Authentication

```text
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/session
```

Protected requests use:

```text
Authorization: Bearer <session-token>
```

### Hosted Zones

```text
GET    /api/hosted-zones
GET    /api/hosted-zones/{id}
POST   /api/hosted-zones
PUT    /api/hosted-zones/{id}
DELETE /api/hosted-zones/{id}
```

List supports `page`, `page_size` and `search`.

### DNS Records

```text
GET    /api/hosted-zones/{zone_id}/records
GET    /api/records/{id}
POST   /api/hosted-zones/{zone_id}/records
PUT    /api/records/{id}
DELETE /api/records/{id}
```

Supported record types:

```text
A, AAAA, CNAME, TXT, MX, NS, PTR, SRV, CAA
```

Validation includes IPv4/IPv6 values, hostname targets, MX priority/hostname format, SRV priority/weight/port/target format, CAA structure, supported routing policies and TTL bounds.

## Local setup — manual

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Health:

```text
http://localhost:8000/api/health
```

### Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Local setup — Docker Compose

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:3000
```

The compose setup stores SQLite under a named Docker volume so local restarts do not remove application data.

## Demo credentials

```text
Email:    demo@route53.local
Password: Route53Demo123
```

## Environment variables

### Frontend

`.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

For production, set it to the public FastAPI URL, for example:

```text
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-DOMAIN/api
```

For the Docker build, `NEXT_PUBLIC_API_URL` is a build argument because Next.js public environment variables are embedded during the build.

### Backend

```text
DATABASE_URL=sqlite:///./route53.db
CORS_ORIGINS=http://localhost:3000
```

With a persistent deployment volume mounted at `/data`:

```text
DATABASE_URL=sqlite:////data/route53.db
CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN
```

## Testing

From the repository root:

```powershell
$env:PYTHONPATH="backend"
python -m pytest -q backend/tests.py
```

The test suite covers:

- Protected API routes
- Login/session/logout lifecycle
- Hosted Zone create/read/update/delete
- DNS record create/read/update/delete
- Search
- Cascade deletion
- Validation for all nine supported record types

## Production build verification

Frontend:

```powershell
cd frontend
npm install
npm run build
```

Backend:

```powershell
cd backend
python -m pytest -q tests.py
```

## Deployment

### Option A — Railway backend + Vercel frontend

1. Push the repository to GitHub.
2. Create a Railway service from the repository.
3. Configure the backend service to use `backend/Dockerfile`.
4. Add a Railway Volume mounted at `/data`.
5. Set:

```text
DATABASE_URL=sqlite:////data/route53.db
CORS_ORIGINS=https://YOUR-VERCEL-DOMAIN
```

6. Deploy and verify:

```text
https://YOUR-RAILWAY-DOMAIN/api/health
```

7. Deploy `frontend/` to Vercel.
8. Set:

```text
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-DOMAIN/api
```

9. Verify login, Hosted Zones, records, CRUD, refresh persistence and logout.

### Option B — Render

`render.yaml` contains separate Docker services for the FastAPI backend and Next.js frontend. The backend is configured with a persistent disk at `/data`.

Set the backend `CORS_ORIGINS` to the final frontend URL and the frontend `NEXT_PUBLIC_API_URL` to the final backend URL.

## Screenshots

Add screenshots from the **deployed application** before submission.

Suggested structure:

```text
## Screenshots

### 1. Login
![Login](docs/screenshots/login.png)

### 2. Hosted Zones
![Hosted Zones](docs/screenshots/hosted-zones.png)

### 3. Create Hosted Zone
![Create Hosted Zone](docs/screenshots/create-hosted-zone.png)

### 4. DNS Records
![DNS Records](docs/screenshots/dns-records.png)

### 5. Create/Edit Record
![Record Form](docs/screenshots/record-form.png)
```

Create the screenshot directory with:

```text
docs/screenshots/
```

## Submission checklist

- [ ] `npm run build` succeeds
- [ ] Backend tests pass
- [ ] Login/logout works
- [ ] Direct protected routes redirect to `/login` when no session cookie exists
- [ ] Hosted Zone CRUD works
- [ ] DNS Record CRUD works
- [ ] All nine required record types are accepted with valid values
- [ ] Search and pagination work
- [ ] SQLite persistence survives restart/deployment volume remount
- [ ] Final UI screenshots added
- [ ] GitHub repository created
- [ ] Public frontend URL created
- [ ] Public backend `/api/health` verified
- [ ] README updated with final URLs

## Scope

This is an AWS Route 53 **experience clone**. It does not perform real DNS resolution, AWS IAM, billing, Organizations, or real AWS API operations. Placeholder pages are provided for Dashboard, Traffic Policies, Health Checks, Resolver and Profiles where the assignment permits placeholders.
