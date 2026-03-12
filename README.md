# FlowCRM

FlowCRM is a CRM platform in progress for managing customer relationships, sales activity, and organization-based user access. The project is being built as a full-stack application with a Django REST API on the backend and a Next.js frontend on the client side.

This repository currently covers the foundation layer of the system: authentication, custom user management, organization membership, and the initial frontend setup. The long-term goal is to grow this into a multi-tenant CRM with leads, deals, pipeline management, tasks, analytics, and deployment-ready infrastructure.

## Why This Project Exists

This project is part portfolio build and part systems design exercise. It focuses on:

- building a full-stack business application instead of a small demo
- practicing backend architecture with Django REST Framework
- structuring a multi-tenant SaaS-style codebase
- connecting a modern React frontend to a secure JWT-based API
- documenting product planning and architecture as the project evolves

## Current Status

Implemented today:

- custom Django user model with email-based authentication
- JWT login and token refresh using Simple JWT
- authenticated `me` endpoint
- logout flow with refresh-token blacklisting
- `Organization` and `Membership` models to support multi-tenant ownership
- Next.js frontend scaffold for the client application
- planning documents for architecture, structure, and sprint roadmap

Planned next:

- registration flow
- lead and deal management
- drag-and-drop sales pipeline
- activities and tasks
- analytics dashboard
- Docker-based deployment workflow

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- Simple JWT
- PostgreSQL

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Project Structure

```text
FlowCrm/
|-- backend/     # Django API, models, auth endpoints, app modules
|-- frontend/    # Next.js app
|-- docs/        # architecture notes, sprint plan, project structure
|-- docker/      # container-related assets
|-- scripts/     # helper scripts
```

## Implemented API Endpoints

Base path: `/api/auth/`

- `POST /login/` - obtain access and refresh tokens
- `POST /refresh/` - refresh an access token
- `GET /me/` - return the authenticated user
- `POST /logout/` - blacklist the submitted refresh token

## Local Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd FlowCrm
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` with values like:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=flowcrm
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
```

Run migrations and start the API:

```bash
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000/`.

### 3. Frontend setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000/`.

## Architecture Notes

The backend is organized by app domain so features can grow without collapsing into a single large module. The current design already introduces the core SaaS concepts:

- a custom user model for auth flexibility
- organization ownership for tenant separation
- membership roles for future permissions and RBAC
- token-based authentication for frontend and API integration

The repository also includes planning documents in [`docs/architecture.md`](docs/architecture.md), [`docs/sprints.md`](docs/sprints.md), and [`docs/structure.md`](docs/structure.md).

## What Recruiters Should Notice

- This is not just a UI clone; it is structured as a business application with backend domain modeling.
- The codebase shows deliberate planning for multi-tenancy, authentication, and future role-based access.
- The project includes architecture and sprint documentation, which reflects engineering process, not only implementation.
- The current code is early-stage, but the system is being built with production-style patterns in mind.

## Roadmap

- add registration and onboarding flow
- enforce organization-scoped access across resources
- implement CRM entities such as leads, deals, stages, and tasks
- build the dashboard and analytics layer
- add tests and CI coverage
- prepare Dockerized local and deployment environments

## License

This project is currently for educational and portfolio use.
