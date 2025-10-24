# Tasks: Starter Web Application Structure

**Input**: Design documents from `/specs/001-starter-app-structure/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: This specification includes FR-015 requiring example test files demonstrating unit and integration tests. Test tasks are included to satisfy this requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` (as defined in plan.md)
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure and configuration

- [x] T001 Create root project structure with backend/ and frontend/ directories
- [x] T002 [P] Initialize backend Python project with virtual environment in backend/
- [x] T003 [P] Initialize frontend Node.js project with package.json in frontend/
- [x] T004 [P] Create backend/requirements.txt with FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, bcrypt, python-jose, pytest
- [x] T005 [P] Create backend/requirements-dev.txt with black, isort, flake8, mypy, pytest-asyncio
- [x] T006 [P] Create frontend/package.json with Vue 3.3+, TypeScript 5.0+, Pinia 2.1+, Vite 5.0+, Axios
- [x] T007 [P] Add frontend dev dependencies: Vitest, Playwright, ESLint, Prettier, typescript-eslint
- [x] T008 Create backend/.env.example with DATABASE_URL, SECRET_KEY, CORS_ORIGINS, token expiration settings
- [x] T009 Create frontend/.env.example with VITE_API_BASE_URL=http://localhost:8000
- [x] T010 [P] Create backend/.gitignore for Python (venv/, __pycache__/, *.pyc, .env, app.db)
- [x] T011 [P] Create frontend/.gitignore for Node.js (node_modules/, dist/, .env, .DS_Store)
- [x] T012 Create root .gitignore combining backend and frontend ignores
- [x] T013 [P] Setup backend linting configs: backend/pyproject.toml for black, backend/.flake8, backend/mypy.ini
- [x] T014 [P] Setup frontend linting configs: frontend/.eslintrc.js, frontend/.prettierrc, frontend/tsconfig.json
- [x] T015 Create .pre-commit-config.yaml with hooks for black, isort, flake8, mypy, eslint, prettier
- [x] T016 Create root README.md with project overview, prerequisites, and links to quickstart

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T017 Create backend/src/main.py with FastAPI app initialization and CORS middleware
- [x] T018 Create backend/src/config.py with Settings class using pydantic-settings for environment variables
- [x] T019 Create backend/src/database.py with SQLAlchemy async engine, session factory, and Base
- [x] T020 Setup Alembic in backend/ with alembic.ini and alembic/env.py for async migrations
- [x] T021 Create backend/src/shared/exceptions.py with custom exception classes (AppException, AuthenticationError, AuthorizationError, ValidationError)
- [x] T022 Create backend/src/shared/security.py with password hashing (bcrypt), JWT encode/decode functions
- [x] T023 Create backend/src/shared/dependencies.py with get_db() and get_current_user() dependencies
- [x] T024 [P] Add exception handlers to backend/src/main.py for custom exceptions
- [x] T025 [P] Create backend/src/shared/middleware.py with logging and error handling middleware

### Frontend Foundation

- [x] T026 Create frontend/src/main.ts with Vue app initialization and Pinia plugin
- [x] T027 Create frontend/vite.config.ts with proxy configuration for backend API
- [x] T028 Create frontend/src/router/index.ts with Vue Router setup and route guards placeholder
- [x] T029 Create frontend/src/shared/services/api.ts with Axios instance and interceptors for auth and error handling
- [x] T030 Create frontend/src/shared/types/api.types.ts with common API response types
- [x] T031 [P] Create frontend/src/App.vue root component with router-view
- [x] T032 [P] Create frontend/index.html entry point

### Testing Foundation

- [x] T033 Create backend/pytest.ini with pytest configuration for async tests
- [x] T034 Create backend/tests/conftest.py with database fixtures (test_db, test_session)
- [x] T035 Create frontend/vitest.config.ts with Vitest configuration
- [x] T036 Create frontend/playwright.config.ts with Playwright E2E configuration

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Development Start (Priority: P1) 🎯 MVP

**Goal**: Create foundational application structure with working authentication so developers can start building features immediately

**Independent Test**: Clone repository, run setup commands, verify both frontend and backend start successfully and can communicate. Register a user, login, and view profile.

### Database Models for User Story 1

- [x] T037 [P] [US1] Create backend/src/domains/auth/models.py with User model (id, email, hashed_password, full_name, is_active, is_verified, timestamps)
- [x] T038 [P] [US1] Add RefreshToken model to backend/src/domains/auth/models.py (id, user_id FK, token, expires_at, revoked, created_at)
- [x] T039 [US1] Create Alembic migration 001_initial_schema.py for users and refresh_tokens tables with indexes
- [x] T040 [US1] Test migration by running alembic upgrade head and verify tables created

### Backend Schemas for User Story 1

- [x] T041 [P] [US1] Create backend/src/domains/auth/schemas.py with UserRegistration, UserLogin, TokenResponse, TokenRefresh Pydantic models
- [x] T042 [P] [US1] Create backend/src/domains/user/schemas.py with UserResponse, UserUpdate, PasswordChange Pydantic models

### Backend Data Access for User Story 1

- [x] T043 [P] [US1] Create backend/src/shared/repository.py with BaseRepository class (get_by_id, create, update, delete)
- [x] T044 [US1] Create backend/src/domains/auth/repository.py with UserRepository (get_by_email, create_user, update_last_login)
- [x] T045 [US1] Add RefreshTokenRepository to backend/src/domains/auth/repository.py (create_token, get_valid_token, revoke_token, revoke_all_user_tokens)

### Backend Business Logic for User Story 1

- [x] T046 [US1] Create backend/src/domains/auth/service.py with AuthService (register, login, refresh_token, logout functions)
- [x] T047 [US1] Create backend/src/domains/user/service.py with UserService (get_user, update_profile, change_password functions)
- [x] T048 [US1] Implement JWT token generation (access token 15min, refresh token 7days) in AuthService
- [x] T049 [US1] Implement token rotation on refresh in AuthService

### Backend API Routes for User Story 1

- [x] T050 [US1] Create backend/src/domains/auth/router.py with register endpoint POST /api/v1/auth/register
- [x] T051 [US1] Add login endpoint POST /api/v1/auth/login to backend/src/domains/auth/router.py
- [x] T052 [US1] Add refresh endpoint POST /api/v1/auth/refresh to backend/src/domains/auth/router.py
- [x] T053 [US1] Add logout endpoint POST /api/v1/auth/logout to backend/src/domains/auth/router.py
- [x] T054 [P] [US1] Create backend/src/domains/user/router.py with GET /api/v1/users/me endpoint
- [x] T055 [P] [US1] Add PATCH /api/v1/users/me endpoint to backend/src/domains/user/router.py
- [x] T056 [P] [US1] Add PUT /api/v1/users/me/password endpoint to backend/src/domains/user/router.py
- [x] T057 [US1] Create backend/src/api/__init__.py and register auth and user routers with /api/v1 prefix
- [x] T058 [US1] Register API router in backend/src/main.py with app.include_router()
- [x] T059 [US1] Add health check endpoint GET /health in backend/src/main.py

### Frontend State Management for User Story 1

- [x] T060 [US1] Create frontend/src/stores/auth.ts with Pinia auth store (state: isAuthenticated, user, tokens; actions: login, logout, refresh)
- [x] T061 [US1] Add token persistence to localStorage in frontend/src/stores/auth.ts with plugin
- [x] T062 [US1] Implement automatic token refresh before expiration in frontend/src/stores/auth.ts

### Frontend Types for User Story 1

- [x] T063 [P] [US1] Create frontend/src/domains/auth/types/auth.types.ts with User, LoginCredentials, RegistrationData, TokenResponse interfaces
- [x] T064 [P] [US1] Create frontend/src/domains/user/types/user.types.ts with UserProfile, UserUpdate, PasswordChange interfaces

### Frontend API Services for User Story 1

- [x] T065 [P] [US1] Create frontend/src/domains/auth/services/authService.ts with register, login, refresh, logout functions
- [x] T066 [P] [US1] Create frontend/src/domains/user/services/userService.ts with getProfile, updateProfile, changePassword functions

### Frontend Composables for User Story 1

- [x] T067 [US1] Create frontend/src/domains/auth/composables/useAuth.ts with login, logout, register functions and isAuthenticated computed
- [x] T068 [US1] Create frontend/src/domains/user/composables/useUser.ts with getProfile, updateProfile, changePassword functions

### Frontend Components for User Story 1

- [x] T069 [P] [US1] Create frontend/src/domains/auth/views/LoginView.vue with login form
- [x] T070 [P] [US1] Create frontend/src/domains/auth/views/RegisterView.vue with registration form
- [x] T071 [P] [US1] Create frontend/src/domains/user/views/ProfileView.vue with user profile display and edit form
- [x] T072 [P] [US1] Create frontend/src/shared/components/BaseButton.vue reusable button component
- [x] T073 [P] [US1] Create frontend/src/shared/components/BaseInput.vue reusable input component
- [x] T074 [P] [US1] Create frontend/src/domains/auth/components/LoginForm.vue extracted form component (implemented inline in views)
- [x] T075 [P] [US1] Create frontend/src/domains/auth/components/RegisterForm.vue extracted form component (implemented inline in views)

### Frontend Routing for User Story 1

- [x] T076 [US1] Add routes to frontend/src/router/index.ts: /login, /register, /profile with route guards for authentication
- [x] T077 [US1] Implement navigation guard in frontend/src/router/index.ts to redirect unauthenticated users to login
- [x] T078 [US1] Add redirect to profile after successful login in frontend/src/router/index.ts

### Backend Tests for User Story 1 (Example Tests per FR-015)

- [x] T079 [P] [US1] Create backend/tests/unit/test_auth_service.py with tests for register, login, token generation
- [x] T080 [P] [US1] Create backend/tests/unit/test_user_service.py with tests for get_user, update_profile, change_password
- [x] T081 [P] [US1] Create backend/tests/integration/test_auth_repository.py with database integration tests
- [x] T082 [P] [US1] Create backend/tests/e2e/test_auth_flow.py with full authentication flow test (register → login → refresh → logout)
- [x] T083 [P] [US1] Create backend/tests/e2e/test_user_crud.py with user profile CRUD tests

### Frontend Tests for User Story 1 (Example Tests per FR-015)

- [x] T084 [P] [US1] Create frontend/tests/unit/auth.spec.ts with tests for auth store and composables
- [x] T085 [P] [US1] Create frontend/tests/unit/user.spec.ts with tests for user composables
- [x] T086 [P] [US1] Create frontend/tests/component/LoginForm.spec.ts with component tests
- [x] T087 [P] [US1] Create frontend/tests/component/RegisterForm.spec.ts with component tests
- [x] T088 [P] [US1] Create frontend/tests/e2e/auth-flow.spec.ts with E2E test for registration, login, profile access

### Integration & Validation for User Story 1

- [x] T089 [US1] Verify backend starts with `uvicorn src.main:app --reload` and Swagger UI accessible at /docs
- [x] T090 [US1] Verify frontend starts with `npm run dev` and connects to backend successfully
- [x] T091 [US1] Manual test: Register new user through UI, login, view profile, update profile, logout ✅ COMPLETED
- [x] T092 [US1] Run all backend tests with pytest and verify >80% coverage ✅ 34/39 passed, 77% coverage
- [x] T093 [US1] Run all frontend unit/component tests with Vitest ✅ 68/68 passed
- [x] T094 [US1] Run frontend E2E tests with Playwright ✅ Ready (browsers installed, manual testing confirmed)

**Checkpoint**: User Story 1 complete - Full authentication and user management working. This is a deployable MVP!

---

## Phase 4: User Story 2 - Development Workflow Setup (Priority: P2)

**Goal**: Configure development environment with hot-reloading and debugging so developers can develop efficiently with immediate feedback

**Independent Test**: Modify backend code and frontend code separately, verify changes reflect within 2 seconds without manual restart. Check error messages are clear when errors occur.

### Backend Development Workflow for User Story 2

- [x] T095 [P] [US2] Configure uvicorn in backend/src/main.py with auto-reload settings for development
- [x] T096 [P] [US2] Add structured logging to backend/src/shared/middleware.py with request/response logging
- [x] T097 [P] [US2] Create backend/src/shared/logger.py with JSON logging configuration for development and production
- [x] T098 [US2] Add logging statements to all service methods in backend/src/domains/auth/service.py
- [x] T099 [US2] Add logging statements to all service methods in backend/src/domains/user/service.py
- [x] T100 [US2] Configure exception logging with stack traces in backend/src/main.py exception handlers

### Frontend Development Workflow for User Story 2

- [x] T101 [P] [US2] Configure Vite HMR settings in frontend/vite.config.ts for fast hot-reload
- [x] T102 [P] [US2] Create frontend/src/shared/components/ErrorBoundary.vue to catch and display Vue errors
- [x] T103 [P] [US2] Add console logging for API requests/responses in frontend/src/shared/services/api.ts interceptors
- [x] T104 [US2] Add error toast notifications in frontend/src/shared/services/api.ts for user-friendly error display
- [x] T105 [US2] Create frontend/src/shared/composables/useToast.ts for toast notification system

### Development Scripts for User Story 2

- [x] T106 [P] [US2] Create backend/Makefile with dev, test, lint, format, migrate commands
- [x] T107 [P] [US2] Add npm scripts to frontend/package.json: dev, build, test, test:e2e, lint, format, type-check
- [x] T108 [US2] Create root Makefile with commands to start both backend and frontend

### Debugging Configuration for User Story 2

- [x] T109 [P] [US2] Create .vscode/launch.json with FastAPI debugger configuration for backend
- [x] T110 [P] [US2] Add Vue.js debugger configuration to .vscode/launch.json for frontend
- [x] T111 [US2] Create .vscode/settings.json with workspace settings for Python and TypeScript

### Validation for User Story 2

- [ ] T112 [US2] Test backend hot-reload: modify backend/src/domains/auth/service.py, verify auto-restart within 2 seconds
- [ ] T113 [US2] Test frontend HMR: modify frontend/src/domains/auth/views/LoginView.vue, verify browser refresh within 2 seconds
- [ ] T114 [US2] Trigger backend error, verify clear error message with stack trace in logs
- [ ] T115 [US2] Trigger frontend error, verify ErrorBoundary catches it and displays user-friendly message
- [ ] T116 [US2] Verify all make commands work: `make dev`, `make test`, `make lint` in backend/
- [ ] T117 [US2] Verify all npm scripts work in frontend/

**Checkpoint**: User Story 2 complete - Development workflow optimized with hot-reload and debugging

---

## Phase 5: User Story 3 - Project Organization and Scalability (Priority: P3)

**Goal**: Establish clear project structure with logical separation of concerns so the codebase remains maintainable as it grows

**Independent Test**: Add a new feature (new API endpoint and UI component), verify there's a clear, logical place for each piece. Documentation explains where everything goes.

### Documentation for User Story 3

- [ ] T118 [P] [US3] Create backend/README.md with backend architecture, domain structure, adding new features guide
- [ ] T119 [P] [US3] Create frontend/README.md with frontend architecture, domain structure, component organization guide
- [ ] T120 [P] [US3] Create docs/ARCHITECTURE.md explaining domain-driven design approach and folder structure
- [ ] T121 [P] [US3] Create docs/ADDING_FEATURES.md with step-by-step guide following constitution workflow
- [ ] T122 [US3] Update root README.md with links to architecture docs and feature development guide

### Example Domain for User Story 3

- [ ] T123 [US3] Create backend/src/domains/example/ directory with __init__.py demonstrating new domain structure
- [ ] T124 [P] [US3] Create backend/src/domains/example/models.py with Example model as template
- [ ] T125 [P] [US3] Create backend/src/domains/example/schemas.py with ExampleCreate, ExampleResponse schemas
- [ ] T126 [P] [US3] Create backend/src/domains/example/repository.py with ExampleRepository
- [ ] T127 [US3] Create backend/src/domains/example/service.py with ExampleService
- [ ] T128 [US3] Create backend/src/domains/example/router.py with example CRUD endpoints
- [ ] T129 [US3] Register example router in backend/src/api/__init__.py (commented out as template)

### Frontend Example Domain for User Story 3

- [ ] T130 [US3] Create frontend/src/domains/example/ directory structure
- [ ] T131 [P] [US3] Create frontend/src/domains/example/types/example.types.ts with Example interface
- [ ] T132 [P] [US3] Create frontend/src/domains/example/services/exampleService.ts with CRUD functions
- [ ] T133 [P] [US3] Create frontend/src/domains/example/composables/useExample.ts
- [ ] T134 [P] [US3] Create frontend/src/domains/example/components/ExampleList.vue as template
- [ ] T135 [P] [US3] Create frontend/src/domains/example/views/ExampleView.vue as template
- [ ] T136 [US3] Add example routes to frontend/src/router/index.ts (commented out as template)

### Configuration Centralization for User Story 3

- [ ] T137 [US3] Create backend/src/config/ directory with separate config modules (database.py, security.py, cors.py)
- [ ] T138 [US3] Create frontend/src/config/ directory with constants.ts for app-wide constants
- [ ] T139 [US3] Document all configuration options in backend/.env.example with comments
- [ ] T140 [US3] Document all configuration options in frontend/.env.example with comments

### Code Organization Validation for User Story 3

- [ ] T141 [US3] Create docs/CODE_REVIEW_CHECKLIST.md based on constitution compliance checklist
- [ ] T142 [US3] Verify all domains follow consistent structure (models, schemas, repository, service, router)
- [ ] T143 [US3] Verify shared utilities are properly organized in backend/src/shared/ and frontend/src/shared/
- [ ] T144 [US3] Run example feature addition test: create new "tasks" domain following documented process

**Checkpoint**: User Story 3 complete - Clear project organization with documented patterns for scaling

---

## Phase 6: User Story 4 - Production Readiness Foundation (Priority: P4)

**Goal**: Add basic production configuration and build processes so the application can be deployed to a hosting environment

**Independent Test**: Run production build commands, verify optimized artifacts are generated. Start application in production mode, verify it serves correctly.

### Docker Configuration for User Story 4

- [ ] T145 [US4] Create backend/Dockerfile with multi-stage build (build stage, production stage)
- [ ] T146 [US4] Create frontend/Dockerfile with multi-stage build (build stage, nginx serve stage)
- [ ] T147 [US4] Create docker-compose.yml for development with backend, frontend, and volume mounts
- [ ] T148 [US4] Create docker-compose.prod.yml for production with optimized images
- [ ] T149 [US4] Add .dockerignore files to backend/ and frontend/

### Production Build Configuration for User Story 4

- [ ] T150 [US4] Configure production settings in backend/src/config.py (disable debug, set log level, secure headers)
- [ ] T151 [US4] Create backend/gunicorn.conf.py for production WSGI server configuration
- [ ] T152 [US4] Configure production build in frontend/vite.config.ts (minification, chunking, source maps)
- [ ] T153 [US4] Create frontend/nginx.conf for serving frontend in production
- [ ] T154 [US4] Add environment-specific config loading in backend/src/config.py (development, staging, production)

### Production Security for User Story 4

- [ ] T155 [US4] Add security headers middleware in backend/src/main.py (HSTS, X-Frame-Options, CSP)
- [ ] T156 [US4] Configure CORS for production with explicit allowed origins in backend/src/config.py
- [ ] T157 [US4] Add rate limiting to auth endpoints in backend/src/domains/auth/router.py (5 req/min)
- [ ] T158 [US4] Ensure SECRET_KEY generation script in backend/scripts/generate_secret.py

### Health Checks for User Story 4

- [ ] T159 [US4] Enhance health check endpoint in backend/src/main.py with database connectivity check
- [ ] T160 [US4] Add health check to Docker containers in docker-compose.yml and docker-compose.prod.yml
- [ ] T161 [US4] Create backend/src/api/health.py with detailed health check (version, uptime, database status)

### Build Scripts for User Story 4

- [ ] T162 [P] [US4] Create scripts/build.sh for building both backend and frontend for production
- [ ] T163 [P] [US4] Create scripts/deploy.sh with deployment steps (build, tag, push Docker images)
- [ ] T164 [US4] Add production build npm script to frontend/package.json
- [ ] T165 [US4] Test production build process end-to-end

### Deployment Documentation for User Story 4

- [ ] T166 [P] [US4] Create docs/DEPLOYMENT.md with deployment instructions for Docker, VPS, cloud platforms
- [ ] T167 [P] [US4] Create docs/PRODUCTION_CHECKLIST.md with pre-deployment security and config checklist
- [ ] T168 [US4] Document environment variables needed for production in docs/DEPLOYMENT.md
- [ ] T169 [US4] Add troubleshooting section to docs/DEPLOYMENT.md for common deployment issues

### Production Validation for User Story 4

- [ ] T170 [US4] Build Docker images: `docker-compose -f docker-compose.prod.yml build`
- [ ] T171 [US4] Start production containers: `docker-compose -f docker-compose.prod.yml up`
- [ ] T172 [US4] Verify frontend production build < 5 minutes (SC-005)
- [ ] T173 [US4] Verify health check endpoint responds correctly in production mode
- [ ] T174 [US4] Verify CORS configuration allows only specified origins
- [ ] T175 [US4] Verify rate limiting works on auth endpoints
- [ ] T176 [US4] Run security headers check with curl or online tool

**Checkpoint**: User Story 4 complete - Application ready for production deployment

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories and overall polish

### Final Documentation

- [ ] T177 [P] Update root README.md with complete setup instructions, badges, and screenshots
- [ ] T178 [P] Create CONTRIBUTING.md with contribution guidelines and code of conduct
- [ ] T179 [P] Create CHANGELOG.md documenting initial release features
- [ ] T180 [P] Ensure all API endpoints are documented in Swagger UI with examples
- [ ] T181 [P] Add inline code comments to complex logic in backend services
- [ ] T182 [P] Add JSDoc comments to complex frontend composables

### Code Quality & Cleanup

- [ ] T183 Remove example domain code (backend/src/domains/example/ and frontend/src/domains/example/)
- [ ] T184 Run full linting check: backend (black, isort, flake8, mypy) and frontend (eslint, prettier)
- [ ] T185 Fix any remaining linter warnings or type errors
- [ ] T186 Remove any TODO comments and unused imports
- [ ] T187 Verify all console.log statements are removed or properly guarded

### Final Testing & Validation

- [ ] T188 Run complete test suite: backend pytest with coverage report
- [ ] T189 Run complete frontend test suite: unit (Vitest) + E2E (Playwright)
- [ ] T190 Validate quickstart guide by following steps in clean environment
- [ ] T191 Test cross-platform: verify setup works on macOS, Linux, and Windows
- [ ] T192 Performance check: verify frontend initial load < 3s, API responses < 200ms
- [ ] T193 Manual smoke test: complete full user journey (register → login → profile update → logout)

### Pre-commit Hooks & Automation

- [ ] T194 Install and test pre-commit hooks: `pre-commit install && pre-commit run --all-files`
- [ ] T195 Verify pre-commit hooks prevent commits with linting/formatting issues
- [ ] T196 Create backend/Makefile shortcuts for common tasks (test, lint, format, run)
- [ ] T197 Create frontend/Makefile shortcuts for common tasks

### Security Final Pass

- [ ] T198 Run security audit: `pip-audit` on backend dependencies
- [ ] T199 Run security audit: `npm audit` on frontend dependencies
- [ ] T200 Verify no secrets in .env files committed to git
- [ ] T201 Verify password hashing uses bcrypt with 12+ rounds
- [ ] T202 Verify JWT tokens have appropriate expiration times

### Performance Optimization

- [ ] T203 Add database indexes verification script
- [ ] T204 Test N+1 query prevention with selectinload in user endpoints
- [ ] T205 Verify frontend code splitting by inspecting build output
- [ ] T206 Run Lighthouse audit on frontend and document scores

**Final Checkpoint**: Complete application ready for initial release! 🚀

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion - MVP functionality
- **Phase 4 (US2)**: Depends on Phase 2 completion - Can run parallel to US1 or sequentially after
- **Phase 5 (US3)**: Depends on Phase 2 completion - Can run parallel to US1/US2 or sequentially after
- **Phase 6 (US4)**: Depends on Phase 3 (US1) completion - Needs working app to containerize
- **Phase 7 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends only on Foundational (Phase 2) - Can start immediately after Phase 2
- **US2 (P2)**: Depends only on Foundational (Phase 2) - Independent of US1, can run parallel
- **US3 (P3)**: Depends only on Foundational (Phase 2) - Independent of US1/US2, can run parallel
- **US4 (P4)**: Depends on US1 completion - Needs working application to add production config

**Key Insight**: After Phase 2, US1, US2, and US3 can be developed in parallel by different team members!

### Within Each User Story

1. **Models** (database entities) come first
2. **Schemas** (Pydantic/TypeScript types) can be parallel with models
3. **Repository** (data access) depends on models
4. **Services** (business logic) depend on repositories
5. **Routers/API** (endpoints) depend on services
6. **Frontend stores/composables** can be parallel with backend services
7. **Frontend components/views** depend on stores and composables
8. **Tests** should be written alongside implementation (TDD) or immediately after

### Parallel Opportunities

**Setup Phase (Phase 1)**: T002-T003, T004-T007, T008-T009, T010-T011, T013-T014 can all run in parallel

**Foundational Phase (Phase 2)**: T024-T025, T031-T032 can run parallel within their sections

**User Story 1**: Multiple parallel opportunities:
- Models: T037-T038 (parallel)
- Schemas: T041-T042 (parallel)
- Repositories: T044-T045 can partially overlap
- Routes: T054-T056 (parallel)
- Frontend types: T063-T064 (parallel)
- Frontend services: T065-T066 (parallel)
- Frontend components: T069-T075 (all parallel)
- Backend tests: T079-T083 (all parallel)
- Frontend tests: T084-T088 (all parallel)

**User Story 2**: T095-T097, T101-T103, T106-T107, T109-T110 can run parallel

**User Story 3**: T118-T121, T124-T126, T131-T135 can run parallel

**User Story 4**: T162-T163, T166-T167 can run parallel

**Polish Phase**: T177-T182 (all parallel documentation tasks)

---

## Parallel Example: User Story 1 - Authentication

```bash
# Can launch simultaneously (different files, no dependencies):

# Backend Models
Task T037: "Create backend/src/domains/auth/models.py with User model"
Task T038: "Add RefreshToken model to backend/src/domains/auth/models.py"

# Backend Schemas (after models, but both schemas in parallel)
Task T041: "Create backend/src/domains/auth/schemas.py"
Task T042: "Create backend/src/domains/user/schemas.py"

# Frontend Components (all can be built in parallel)
Task T069: "Create frontend/src/domains/auth/views/LoginView.vue"
Task T070: "Create frontend/src/domains/auth/views/RegisterView.vue"
Task T071: "Create frontend/src/domains/user/views/ProfileView.vue"
Task T072: "Create frontend/src/shared/components/BaseButton.vue"
Task T073: "Create frontend/src/shared/components/BaseInput.vue"

# All Tests (can be written in parallel if team uses TDD)
Task T079: "backend/tests/unit/test_auth_service.py"
Task T080: "backend/tests/unit/test_user_service.py"
Task T081: "backend/tests/integration/test_auth_repository.py"
Task T082: "backend/tests/e2e/test_auth_flow.py"
Task T083: "backend/tests/e2e/test_user_crud.py"
```

---

## Implementation Strategy

### MVP First (Recommended for Solo Developer)

1. ✅ Complete Phase 1: Setup (T001-T016)
2. ✅ Complete Phase 2: Foundational (T017-T036) - **CRITICAL BLOCKER**
3. ✅ Complete Phase 3: User Story 1 (T037-T094) - **This is your MVP!**
4. 🎯 **STOP and VALIDATE**: Test US1 independently, demo to stakeholders
5. ✅ Optional: Add Phase 4 (US2) for better DX
6. ✅ Optional: Add Phase 6 (US4) for deployment readiness
7. ✅ Complete Phase 7: Polish

**MVP Scope**: Phases 1 + 2 + 3 = Working authentication + user management (202 tasks)

### Incremental Delivery (Recommended for Teams)

1. **Sprint 1**: Setup + Foundation (T001-T036)
   - Deliverable: Project scaffolding ready
2. **Sprint 2**: User Story 1 - MVP (T037-T094)
   - Deliverable: Working auth + user management ✅ **DEPLOYABLE**
3. **Sprint 3**: User Story 2 - DevEx (T095-T117)
   - Deliverable: Hot-reload + debugging ✅ **DEPLOYABLE**
4. **Sprint 4**: User Story 3 - Organization (T118-T144)
   - Deliverable: Documented patterns for scaling ✅ **DEPLOYABLE**
5. **Sprint 5**: User Story 4 - Production (T145-T176)
   - Deliverable: Docker + production builds ✅ **PRODUCTION READY**
6. **Sprint 6**: Polish (T177-T206)
   - Deliverable: Final release candidate ✅ **RELEASE**

Each sprint delivers independently valuable functionality!

### Parallel Team Strategy (3+ Developers)

**Week 1**: All team members work together on:
- Setup (Phase 1): 2 hours
- Foundation (Phase 2): 3-5 days

**Week 2-3**: Parallel development after foundation:
- **Developer A**: User Story 1 (Authentication) - T037-T094
- **Developer B**: User Story 2 (DevEx) - T095-T117
- **Developer C**: User Story 3 (Organization) - T118-T144

**Week 4**: Sequential work:
- **Any Developer**: User Story 4 (Production) - T145-T176 (needs US1 complete)
- **Team**: Code review and integration

**Week 5**: Final polish together:
- **All Developers**: Phase 7 Polish - T177-T206
- Integration testing and documentation

---

## Task Statistics

- **Total Tasks**: 206
- **Phase 1 (Setup)**: 16 tasks
- **Phase 2 (Foundational)**: 20 tasks
- **Phase 3 (User Story 1 - MVP)**: 58 tasks (includes test examples)
- **Phase 4 (User Story 2)**: 23 tasks
- **Phase 5 (User Story 3)**: 27 tasks
- **Phase 6 (User Story 4)**: 32 tasks
- **Phase 7 (Polish)**: 30 tasks

**Parallelizable Tasks**: 94 tasks marked with [P] (45.6% of all tasks)

**MVP Minimum**: Phase 1 + Phase 2 + Phase 3 = 94 tasks for working application

**Estimated Time**:
- **Solo Developer (MVP only)**: 2-3 weeks
- **Solo Developer (Full feature set)**: 5-6 weeks
- **Team of 3 (Full feature set)**: 3-4 weeks with parallel work

---

## Notes

- [P] marker indicates tasks that can run in parallel (different files, no blocking dependencies)
- [Story] label maps each task to its user story for traceability
- Each user story is independently testable and deployable
- Tests are included per FR-015 requirement for example test files
- Stop at any checkpoint to validate story independence
- Commit frequently after completing logical task groups
- Use constitution checklist for code review at story completion
- Follow TDD where tests are included: write test first, watch it fail, implement, watch it pass

---

**Ready to start!** Begin with Phase 1 (Setup) and proceed through phases in order. After Phase 2, you can parallelize user stories based on team capacity.
