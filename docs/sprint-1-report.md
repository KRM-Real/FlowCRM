# Sprint 1 Implementation Report

This report documents the work completed to implement Sprint 1.1, Sprint 1.2, and Sprint 1.3 for FlowCRM across the backend and frontend.

## Overview

Sprint 1 was completed with three major goals:

1. Finish backend authentication and organization foundations.
2. Standardize organization-scoped access control for multi-tenant behavior.
3. Replace the placeholder frontend with a working authentication-first interface.

The implementation now provides:

- UUID-based custom users
- app-owned authentication endpoints
- `httpOnly` cookie-based JWT authentication
- reusable organization-scoping patterns
- frontend login, registration, and dashboard routes
- backend test coverage for auth, memberships, and leads access

---

## Sprint 1.1: Backend Setup (Auth + Organization)

### Goal Achieved

Sprint 1.1 required the backend to support user authentication, organization ownership foundations, and JWT-based login flow.

### Files Updated

#### [backend/apps/accounts/models.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/models.py)

Updated the custom `User` model:

- changed the primary key from the default integer to `UUIDField`
- kept email as the authentication identity with `USERNAME_FIELD = "email"`
- preserved compatibility with Django’s `AbstractUser`

This brings the user model in line with the Sprint 1.1 requirement for UUID-based identity.

#### [backend/apps/accounts/migrations/0001_initial.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/migrations/0001_initial.py)

Adjusted the initial migration to match the new UUID-based user model:

- replaced the original `BigAutoField` user primary key with `UUIDField`

This ensures schema generation matches the actual model design.

#### [backend/apps/accounts/serializers.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/serializers.py)

Reworked the serializer layer for authentication:

- added `RegisterSerializer`
  - validates email uniqueness
  - validates password input
  - creates a new user
- added `LoginSerializer`
  - validates email and password
  - authenticates against Django auth
- added `AuthUserSerializer`
  - returns the authenticated user shape used by the frontend
- added `MembershipSummarySerializer`
  - includes membership details for organization-aware frontend rendering
- added `RegisterResponseSerializer`
  - standardizes the registration success response

This file now owns the auth request and response contract rather than relying on raw SimpleJWT defaults.

#### [backend/apps/accounts/services.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/services.py)

Added a new service module:

- introduced `generate_unique_username(email)`
- auto-generates usernames from email addresses
- avoids collisions by appending a numeric suffix

This supports registration while keeping the underlying Django user creation flow valid.

#### [backend/apps/accounts/views.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/views.py)

Replaced the earlier minimal auth flow with app-owned views:

- added `RegisterView`
  - accepts registration payload
  - creates a user
  - returns a success response without tokens
- added `LoginView`
  - authenticates user credentials
  - creates SimpleJWT tokens
  - writes access and refresh tokens into `httpOnly` cookies
  - returns the authenticated user payload
- kept `MeView` and expanded it
  - now returns user and membership data
- added `RefreshView`
  - reads the refresh token from the refresh cookie
  - rotates and resets auth cookies
  - handles invalid and blacklisted tokens cleanly
- updated `LogoutView`
  - blacklists the refresh token when present
  - clears the auth cookies

Also added helper functions:

- `set_auth_cookies`
- `clear_auth_cookies`

These centralize cookie behavior and keep the auth endpoints consistent.

#### [backend/apps/accounts/urls.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/urls.py)

Updated the auth routes:

- added `POST /api/auth/register/`
- changed login to app-owned `POST /api/auth/login/`
- changed refresh to app-owned `POST /api/auth/refresh/`
- kept `GET /api/auth/me/`
- kept `POST /api/auth/logout/`

This removed the dependency on the default `TokenObtainPairView` and `TokenRefreshView` as the public API surface.

#### [backend/apps/accounts/admin.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/admin.py)

Improved the admin configuration for the custom user:

- added useful `list_display`
- added `ordering`
- grouped admin form fields with explicit `fieldsets`
- exposed `id` as a readonly field

This makes the user model easier to manage through Django admin.

#### [backend/config/settings.py](c:/Users/realk/Desktop/FlowCrm/backend/config/settings.py)

Expanded backend configuration to support cookie auth and frontend integration:

- added `AUTH_COOKIE_ACCESS`
- added `AUTH_COOKIE_REFRESH`
- added `AUTH_COOKIE_SECURE`
- added `AUTH_COOKIE_SAMESITE`
- added `AUTH_COOKIE_DOMAIN`
- added `AUTH_COOKIE_PATH`
- added `FRONTEND_URL`
- added `CORS_ALLOWED_ORIGINS`
- added `CSRF_TRUSTED_ORIGINS`
- registered custom cookie authentication ahead of standard JWT auth
- added local SQLite fallback for test runs

These settings make local development and test execution much easier while supporting the Sprint 1 frontend requirements.

#### [backend/apps/common/authentication.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/common/authentication.py)

Added custom DRF authentication logic:

- created `CookieJWTAuthentication`
- reads JWT access token from the configured cookie
- validates the token using SimpleJWT
- authenticates the request without requiring an `Authorization` header

This is the key integration point for `httpOnly` cookie-based auth.

#### [backend/apps/common/middleware.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/common/middleware.py)

Added a lightweight CORS middleware:

- handles allowed origins from settings
- supports credentials
- supports browser preflight `OPTIONS` requests

This enables the frontend to call the backend with cookies during local development.

#### [backend/apps/accounts/tests.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/accounts/tests.py)

Added backend auth test coverage for:

- registration creates a UUID user
- duplicate email is rejected
- login sets auth cookies
- `/me` returns the authenticated user with memberships
- anonymous `/me` is rejected
- refresh rotates refresh cookies
- logout clears cookies and invalidates refresh token reuse

This file provides direct test verification for the Sprint 1.1 backend requirements.

---

## Sprint 1.2: Organization Isolation

### Goal Achieved

Sprint 1.2 required users to be restricted to organization-specific data access. The implementation introduced reusable organization-scoping patterns and aligned the current lead feature with them.

### Files Updated

#### [backend/apps/common/models.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/common/models.py)

Added a reusable abstract base model:

- kept `TimeStampedModel`
- added `OrganizationScopedModel`
  - includes `organization` foreign key
  - inherits timestamp fields

This provides the shared structure needed for future organization-owned models.

#### [backend/apps/common/mixins.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/common/mixins.py)

Added `OrganizationContextMixin`:

- resolves organization from the route parameter
- exposes `get_organization()`
- exposes `filter_organization_queryset()`
- exposes `get_organization_object()`

This reduces repeated tenant-filtering logic and creates a reusable access pattern for later apps.

#### [backend/apps/organizations/views.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/organizations/views.py)

Refactored membership views to use the shared organization context pattern:

- updated list/create membership view to use organization-scoped queryset filtering
- updated detail membership view to use organization-scoped queryset filtering
- added stable ordering for pagination consistency
- preserved permission behavior for member reads and admin writes

This file now follows a consistent tenant-scoping structure instead of manual per-view organization handling.

#### [backend/apps/organizations/serializers.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/organizations/serializers.py)

Updated serializer typing to match the new UUID user primary key:

- changed `user_id` in membership output from integer to UUID

This keeps API output accurate after the user model primary key change.

#### [backend/apps/organizations/tests.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/organizations/tests.py)

Added membership and org access tests:

- member can list organization members
- outsider cannot access another organization’s members
- admin can create a membership
- non-admin cannot create a membership
- last admin cannot be deleted

This validates the membership-based access model that Sprint 1.2 depends on.

#### [backend/apps/leads/models.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/leads/models.py)

Aligned `Lead` with the shared org-owned model pattern:

- changed `Lead` to inherit from `OrganizationScopedModel`
- kept existing lead fields intact
- preserved lead indexes and ordering

This turns the lead feature into the first concrete example of the shared multi-tenant base model.

#### [backend/apps/leads/views.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/leads/views.py)

Refactored lead view behavior to use the new organization mixin:

- added `OrganizationContextMixin`
- removed ad hoc organization lookup code
- kept member-only reads
- kept manager/admin write access
- preserved organization-aware list, retrieve, create, and update behavior

This makes the lead viewset consistent with the new organization isolation structure.

#### [backend/apps/leads/selectors.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/leads/selectors.py)

Kept the selector-based lead querying approach and aligned it with the organization-scoped lead design.

This file continues to provide filtered lead lookup by organization and lead ID.

#### [backend/apps/common/pagination.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/common/pagination.py)

Fixed pagination configuration:

- changed `page_query_param` to `page_size_query_param`

This corrects the page-size behavior for paginated API responses.

#### [backend/apps/leads/migrations/0001_initial.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/leads/migrations/0001_initial.py)

Updated the initial lead migration:

- aligned the `organization` field definition with the current shared org-owned model structure

This keeps migration checks clean after the shared model change.

#### [backend/apps/leads/tests.py](c:/Users/realk/Desktop/FlowCrm/backend/apps/leads/tests.py)

Expanded lead access tests to verify organization isolation:

- member can list only own-organization leads
- non-member cannot access another organization’s leads
- manager can create a lead
- rep cannot create a lead
- lead detail lookup is scoped to the organization in the route

This validates the Sprint 1.2 organization-scoped data rules using the current lead feature.

---

## Sprint 1.3: Frontend Setup (Next.js)

### Goal Achieved

Sprint 1.3 required the frontend to support authentication flow, protected routes, and a usable app shell. The placeholder Next.js starter content was replaced with a FlowCRM-specific interface.

### Files Updated

#### [frontend/app/page.tsx](c:/Users/realk/Desktop/FlowCrm/frontend/app/page.tsx)

Replaced the default starter page:

- reads the auth cookie on load
- redirects authenticated users to `/dashboard`
- redirects unauthenticated users to `/login`

This makes the root route behave like a real application entry point.

#### [frontend/app/login/page.tsx](c:/Users/realk/Desktop/FlowCrm/frontend/app/login/page.tsx)

Added a complete login page:

- controlled form inputs
- simple validation
- cookie-auth login request
- inline error display
- redirect to dashboard after successful login

This page is the primary entry point for returning users.

#### [frontend/app/register/page.tsx](c:/Users/realk/Desktop/FlowCrm/frontend/app/register/page.tsx)

Added a complete registration page:

- first name field
- last name field
- email field
- password field
- form validation
- success messaging after account creation

This page lets new users create an account before an organization admin assigns them membership.

#### [frontend/app/dashboard/page.tsx](c:/Users/realk/Desktop/FlowCrm/frontend/app/dashboard/page.tsx)

Added the initial dashboard shell:

- fetches the current user from `/api/auth/me/`
- shows current identity information
- shows memberships returned by the backend
- supports logout action
- redirects unauthenticated users back to login

This is the first protected application page and forms the base for later dashboard work.

#### [frontend/lib/api-client.ts](c:/Users/realk/Desktop/FlowCrm/frontend/lib/api-client.ts)

Added a shared frontend API client:

- always sends credentials with requests
- parses JSON responses
- throws structured API errors
- attempts refresh automatically when a request receives `401`

This centralizes backend communication and reduces auth duplication in UI pages.

#### [frontend/lib/auth.ts](c:/Users/realk/Desktop/FlowCrm/frontend/lib/auth.ts)

Added auth-specific client functions:

- `login`
- `register`
- `getCurrentUser`
- `logout`

This separates auth behavior from presentation code and keeps auth page logic small.

#### [frontend/lib/env.ts](c:/Users/realk/Desktop/FlowCrm/frontend/lib/env.ts)

Added frontend environment helpers:

- backend API base URL
- access cookie name

This keeps the frontend configuration centralized.

#### [frontend/types/auth.ts](c:/Users/realk/Desktop/FlowCrm/frontend/types/auth.ts)

Added auth-related TypeScript types:

- `AuthUser`
- `MembershipSummary`
- `LoginInput`
- `RegisterInput`

This improves type safety for frontend auth flow and dashboard rendering.

#### [frontend/proxy.ts](c:/Users/realk/Desktop/FlowCrm/frontend/proxy.ts)

Added route protection and redirect logic:

- blocks unauthenticated requests to `/dashboard`
- redirects authenticated users away from `/login`
- redirects authenticated users away from `/register`

This gives the frontend protected-route behavior without exposing token storage to client code.

#### [frontend/app/layout.tsx](c:/Users/realk/Desktop/FlowCrm/frontend/app/layout.tsx)

Updated the root layout:

- changed metadata from default Next.js starter values to FlowCRM-specific values
- replaced default font setup with a more intentional visual identity

This gives the frontend a more product-like presentation.

#### [frontend/app/globals.css](c:/Users/realk/Desktop/FlowCrm/frontend/app/globals.css)

Replaced the starter CSS with full app-level styling:

- background treatment
- form layout
- auth panel layout
- button styles
- dashboard shell layout
- membership cards
- responsive mobile behavior

This transformed the frontend from starter scaffolding into a cohesive auth-first UI.

---

## Verification Performed

The implementation was verified with the following checks:

### Backend

- `.\venv\Scripts\python.exe manage.py test apps.accounts.tests apps.organizations.tests apps.leads.tests`
  - result: 17 tests passed
- `.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run`
  - result: no changes detected

### Frontend

- `npm run lint`
  - result: passed
- `npm run build`
  - result: passed

---

## Final Result

After these changes, Sprint 1 now delivers:

- a UUID-based custom user model
- registration and login owned by the backend application
- cookie-based JWT auth suitable for frontend integration
- reusable organization-scoped backend patterns
- validated membership-based multi-tenant access control
- a functioning frontend with login, registration, and dashboard routes
- test coverage for the core Week 1 backend behaviors

This gives FlowCRM a solid end-of-Week-1 foundation and prepares the codebase for Sprint 2 work.
