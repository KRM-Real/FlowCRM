# FlowCRM Sprint Plan

Target Duration: 8 Weeks  
Stack: Django + Django REST Framework + PostgreSQL + Next.js + TanStack Query + dnd-kit + Docker

This document defines the structured sprint roadmap for building FlowCRM.

Each sprint contains:

- Objective
- Goal
- Tasks
- Expected Output
- Unit Testing
- Logs

This structure allows both engineers and AI agents to understand the development progress and implementation scope.

---

# WEEK 1 — FOUNDATION

---

# Sprint 1.1 — Backend Setup (Auth + Organization)

## Objective
Initialize the backend system and implement authentication with organization ownership.

## Goal
Users can register, login, and belong to an organization with JWT authentication.

## Tasks

### Backend
- Create Django project
- Configure PostgreSQL
- Create custom `User` model (UUID primary key)
- Create `Organization` model
- Link `User -> Organization`
- Install and configure DRF
- Install SimpleJWT
- Create `Register API`
- Create `Login API`

### Learning Tasks
- Understand Django custom user models
- Study JWT authentication (access vs refresh)
- Learn DRF request lifecycle
- Study serializer validation

## Expected Output

- Register endpoint working
- Login endpoint returns JWT tokens
- User belongs to an organization
- PostgreSQL connected

## Unit Testing

Backend tests:

- Test user registration
- Test login returns access + refresh token
- Test user linked to organization
- Test invalid login credentials

Example tools:

- pytest
- Django TestCase
- DRF APIClient

## Logs

Track:

- Migration logs
- Authentication logs
- Token generation logs

---

# Sprint 1.2 — Organization Isolation

## Objective
Implement multi-tenant data isolation.

## Goal
Users can only access data belonging to their organization.

## Tasks

### Backend
- Add `organization_id` to all models
- Create `BaseModel` with organization field
- Override `get_queryset()` in ViewSets
- Apply organization filtering
- Prevent cross-organization access

### Learning Tasks
- Multi-tenant patterns
- DRF permission classes
- Query filtering performance

## Expected Output

- User from Org A cannot access Org B data
- All queries filtered by organization

## Unit Testing

- Test cross-org access blocked
- Test org-filtered queries
- Test permissions for org-scoped endpoints

## Logs

Track:

- Query logs
- Access violation attempts
- Permission validation logs

---

# Sprint 1.3 — Frontend Setup (Next.js)

## Objective
Initialize frontend and connect authentication flow.

## Goal
Frontend login communicates with backend and stores JWT.

## Tasks

### Frontend
- Create Next.js app
- Setup API utility (Axios / Fetch wrapper)
- Create login page
- Store JWT (httpOnly cookie preferred)
- Implement protected routes

### Learning Tasks
- Next.js App Router
- React hooks
- JWT storage security

## Expected Output

- User can login from frontend
- Token stored securely
- Protected routes work

## Unit Testing

Frontend tests:

- Login form validation
- API request handling
- Protected route behavior

Tools:

- React Testing Library
- Jest

## Logs

Track:

- API request logs
- Login success/failure
- Auth token state

---

# WEEK 2 — LEADS

---

# Sprint 2.1 — Lead Backend

## Objective
Implement lead management API.

## Goal
Leads can be created, updated, retrieved, and deleted.

## Tasks

### Backend
- Create `Lead` model
- Create `LeadSerializer`
- Create `LeadViewSet`
- Add filtering (status, owner)
- Add pagination

### Learning Tasks
- Django model relationships
- DRF filtering
- Database indexing

## Expected Output

- Lead CRUD API functional
- Filtering working
- Pagination working

## Unit Testing

- Create lead
- Update lead
- Delete lead
- Filter leads
- Pagination response

## Logs

Track:

- Lead creation logs
- Update operations
- Query performance

---

# Sprint 2.2 — Lead Frontend

## Objective
Build UI for lead management.

## Goal
Users can manage leads through the UI.

## Tasks

### Frontend
- Leads page
- Table component
- Create/Edit modal
- Filtering UI
- Search functionality

### Learning Tasks
- Controlled React forms
- TanStack Query basics
- React state patterns

## Expected Output

- Leads visible in table
- Create/Edit works
- Filters work

## Unit Testing

- Form validation
- Query fetching
- UI state updates

## Logs

Track:

- API requests
- Lead creation UI logs
- Query cache updates

---

# Sprint 2.3 — Lead → Deal Conversion

## Objective
Convert leads into deals.

## Goal
Lead converts into deal using transaction-safe logic.

## Tasks

### Backend
- Create convert endpoint
- Create deal inside transaction
- Update lead status

### Frontend
- Convert button
- Confirmation modal

### Learning Tasks
- Database transactions
- Idempotent APIs

## Expected Output

- Lead converts to deal
- Lead status updated

## Unit Testing

- Conversion endpoint
- Transaction rollback tests
- Duplicate conversion prevention

## Logs

Track:

- Conversion logs
- Transaction failures
- Lead state changes

---

# WEEK 3 — PIPELINE

---

# Sprint 3.1 — Stage Backend

## Objective
Implement pipeline stages.

## Goal
Admin can manage stages.

## Tasks

- Create `Stage` model
- Seed default stages
- CRUD API
- Admin-only access

## Expected Output

- Stages created
- Ordered pipeline stages

## Unit Testing

- Stage creation
- Permission enforcement
- Ordering logic

## Logs

Track stage operations.

---

# Sprint 3.2 — Deal Backend

## Objective
Implement deals with position ordering.

## Goal
Deals can move between stages.

## Tasks

- Create `Deal` model
- Add `position` field
- Implement reorder endpoint
- Handle cross-stage movement
- Update ordering safely

## Expected Output

- Deals ordered correctly
- Move between stages

## Unit Testing

- Move deal within stage
- Move deal across stages
- Position reindexing

## Logs

Track reorder events and race condition issues.

---

# Sprint 3.3 — Kanban UI (Core Portfolio Feature)

## Objective
Build drag-and-drop pipeline.

## Goal
Deals draggable across stages.

## Tasks

- Pipeline page
- Fetch grouped deals
- Implement dnd-kit
- Optimistic updates
- Call reorder API

## Expected Output

- Smooth drag-and-drop
- UI state persists

## Unit Testing

- Drag event handling
- Optimistic UI rollback

## Logs

Track:

- reorder API calls
- state updates
- drag events

---

# WEEK 4 — ACTIVITIES & TASKS

---

# Sprint 4.1 — Activity Backend

## Objective
Add activity tracking.

## Tasks

- Create `Activity` model
- XOR validation (lead OR deal)
- Timeline endpoint

## Expected Output

Activity timeline API.

## Unit Testing

- Validation tests
- Timeline query tests

## Logs

Track activity creation.

---

# Sprint 4.2 — Timeline UI

## Tasks

- Deal detail page
- Timeline component
- Add activity modal

## Expected Output

Activity timeline visible on deals.

---

# Sprint 4.3 — Tasks System

## Tasks

- Task model
- Due date logic
- Overdue badge
- My Tasks page

---

# WEEK 5 — ANALYTICS

---

# Sprint 5.1 — Analytics Backend

## Tasks

- Revenue aggregation
- Conversion rate query
- Group by stage

## Unit Testing

- Aggregation queries
- Analytics API response

---

# Sprint 5.2 — Dashboard UI

## Tasks

- KPI cards
- Bar chart
- Date filters

---

# WEEK 6 — SECURITY

---

# Sprint 6.1 — Role-Based Access Control

## Tasks

- DRF permission classes
- Rep restrictions
- Manager access

---

# Sprint 6.2 — Data Integrity

## Tasks

- Add DB indexes
- Validation rules
- Edge case handling

---

# WEEK 7 — DEPLOYMENT

---

# Sprint 7.1 — Docker

## Tasks

- Write Dockerfiles
- docker-compose
- Environment variables

---

# Sprint 7.2 — Deployment

## Tasks

- Deploy backend
- Deploy frontend
- Configure CORS

---

# WEEK 8 — FINAL POLISH

---

# Sprint 8.1 — CSV Import

- Parse CSV
- Bulk create leads

---

# Sprint 8.2 — Lead Scoring

- Add scoring field
- Basic scoring algorithm

---

# Sprint 8.3 — Documentation

- ER Diagram
- Architecture diagram
- README
- Screenshots

---

# Final Outcome

After completing all sprints, the system will demonstrate:

- Multi-tenant SaaS architecture
- Role-based access control
- Deal pipeline with drag-and-drop
- Analytics dashboard
- Production deployment using Docker