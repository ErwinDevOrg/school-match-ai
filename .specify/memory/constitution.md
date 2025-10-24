# FastAPI + Vue.js Application Constitution

## Core Principles

### I. Domain-Driven Design (NON-NEGOTIABLE)
Code must be organized by business domains, not technical layers. Each domain represents a distinct business concept and contains all layers (models, services, repositories, routes for backend; components, composables, services, views for frontend). Domains must be self-contained with clear boundaries. Cross-domain dependencies require explicit justification and must go through defined interfaces in the shared layer.

### II. Separation of Concerns
Each layer has a single, well-defined responsibility:
- **Backend**: Router (HTTP) → Service (business logic) → Repository (data access) → Database
- **Frontend**: View (page) → Composable (state/logic) → Service (API) → Backend
- Business logic never lives in routers or views
- Database queries never bypass the repository layer
- API calls never bypass the service layer

### III. API Contract First
FastAPI's automatic OpenAPI documentation serves as the contract between frontend and backend. All API changes must:
- Update Pydantic schemas before implementation
- Maintain backward compatibility or version appropriately
- Be reflected in TypeScript types on frontend
- Include request/response examples in documentation

### IV. Test-First Development (NON-NEGOTIABLE)
Every feature follows TDD cycle:
1. Write failing tests that define the expected behavior
2. Get user/stakeholder approval on test scenarios
3. Implement minimum code to make tests pass
4. Refactor while keeping tests green

**Required test coverage:**
- Backend: Service layer business logic, Repository data access patterns, Router integration tests
- Frontend: Composable logic, Component behavior, Service API calls (mocked)
- E2E: Critical user journeys

### V. Type Safety Everywhere
- Backend uses Pydantic models for all API schemas with strict validation
- Frontend uses TypeScript (not JavaScript) with strict mode enabled
- No `any` types without explicit justification
- Shared types between frontend/backend must stay synchronized
- Runtime validation at API boundaries, compile-time validation internally

### VI. Fail Fast and Loud
- Validate inputs at system boundaries (API layer, form submissions)
- Throw meaningful exceptions immediately when invariants are violated
- Never swallow exceptions or return null/undefined for errors
- Use structured error responses with consistent format across all endpoints
- Frontend displays user-friendly error messages while logging technical details

### VII. State Management Discipline
- Backend: Services are stateless; state lives in database or cache
- Frontend: Domain state managed by composables or Pinia stores
- Authentication state centralized in auth store
- No prop drilling beyond 2 levels - use provide/inject or stores
- Side effects (API calls) isolated in composables, not components

## Development Standards

### Code Organization
- **One domain, one folder**: All related code (backend and frontend) grouped by domain
- **File naming**: `snake_case.py` for Python, `camelCase.ts` for TypeScript, `PascalCase.vue` for components
- **Component structure**: Setup script composition API (not options API)
- **Maximum file length**: 300 lines; refactor if exceeded
- **Import order**: External libraries → Core/shared → Domain-specific → Relative imports

### Security Requirements
- All passwords hashed using bcrypt or argon2
- JWT tokens for authentication with appropriate expiration
- CORS configured explicitly - never use wildcard `*` in production
- SQL injection prevention via SQLAlchemy ORM (no raw SQL without review)
- XSS prevention via Vue's automatic escaping (no `v-html` without sanitization)
- Environment variables for all secrets - never commit credentials
- Rate limiting on authentication endpoints

### Performance Standards
- API endpoints respond within 200ms for 95th percentile
- Frontend initial load under 3 seconds on 3G connection
- Database queries optimized with proper indexes
- N+1 query problems must be identified and resolved
- Frontend code splitting by route
- Images optimized and lazy-loaded

## Development Workflow

### Adding a New Feature
1. **Define the domain**: Identify which domain owns this feature
2. **Design API contract**: Create Pydantic schemas and update OpenAPI docs
3. **Write tests**: Backend service tests → Router integration tests → Frontend tests
4. **Implement backend**: Repository → Service → Router (in that order)
5. **Implement frontend**: Types → Service → Composable → Component/View
6. **Integration test**: E2E test for the complete user journey
7. **Code review**: Verify constitution compliance

### Adding a New Domain
1. **Justify the domain**: Explain why it can't fit in existing domains
2. **Define boundaries**: Document what belongs in this domain vs. others
3. **Create structure**: Use domain template for both backend and frontend
4. **Register routes**: Add to main.py and router/index.ts
5. **Document**: Update README with domain purpose and responsibilities
6. **Migration plan**: If moving code from existing domains, create migration checklist

### Code Review Requirements
- All PRs must pass CI/CD pipeline (tests, linting, type checking)
- At least one approval from team member
- Constitution compliance verification checklist:
  - [ ] Code organized by domain
  - [ ] Layers properly separated
  - [ ] Tests written first and passing
  - [ ] Types defined and enforced
  - [ ] Error handling implemented
  - [ ] API contract documented
- Breaking changes require explicit callout and migration guide

## Technology Constraints

### Backend Stack
- **Framework**: FastAPI (async/await)
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL (production), SQLite (local development and testing)
- **Validation**: Pydantic v2
- **Testing**: pytest with pytest-asyncio
- **Database migrations**: Alembic
- **No**: Django, Flask, or synchronous frameworks

### Frontend Stack
- **Framework**: Vue 3 Composition API
- **Language**: TypeScript strict mode
- **Build tool**: Vite
- **State management**: Pinia (not Vuex)
- **HTTP client**: Axios with interceptors
- **Testing**: Vitest + Playwright
- **No**: Options API, JavaScript, or class components

### Infrastructure
- **Python isolation**: All Python applications must run in virtual environments (venv/virtualenv)
  - Virtual environments must be excluded from version control (.gitignore)
  - Dependencies declared in requirements.txt (production) and requirements-dev.txt (development)
  - Python version documented in README and pyproject.toml
  - Activate virtual environment before running any Python commands
- **Containerization**: Docker + docker-compose for development
- **CI/CD**: GitHub Actions with SonarCloud integration
- **Dependency management**: Dependabot enabled
- **Environment parity**: Development environment mirrors production (except database)
- **Database strategy**: 
  - Local development: SQLite for zero-config setup and fast iteration
  - Production: PostgreSQL for performance and production features
  - Alembic migrations must be compatible with both databases
  - Avoid database-specific features unless absolutely necessary
  - Test migrations against both SQLite and PostgreSQL in CI/CD

## Observability

### Logging Requirements
- Structured logging (JSON format) in production
- Log levels: DEBUG (dev only), INFO (operations), WARNING (degraded), ERROR (failures)
- Include correlation IDs for request tracing
- Never log sensitive data (passwords, tokens, PII)

### Monitoring
- FastAPI automatic metrics via `/metrics` endpoint
- Frontend error tracking via error boundary + logging
- Database query performance monitoring
- API response time tracking per endpoint

### Debugging
- Backend: FastAPI automatic interactive docs at `/docs`
- Frontend: Vue DevTools integration
- All errors include stack traces in development
- Reproduction steps required for bug reports

## Governance

### Constitution Authority
This constitution supersedes all other development practices, coding standards, or informal agreements. When in doubt, constitution takes precedence.

### Amendment Process
1. **Proposal**: Document proposed change with justification
2. **Discussion**: Team review of impact and tradeoffs
3. **Approval**: Requires consensus or majority vote
4. **Migration**: Create plan for bringing existing code into compliance
5. **Documentation**: Update constitution with version bump
6. **Communication**: Announce changes to all stakeholders

### Enforcement
- All PRs must pass constitution compliance checklist
- CI/CD pipeline enforces automated checks (linting, types, tests)
- Code review ensures manual verification of principles
- Complexity must be justified - default to simplicity (YAGNI)
- Technical debt that violates constitution must have remediation plan

### Exceptions
Exceptions to constitution principles require:
- Written justification explaining why compliance is impossible
- Approval from at least two senior team members
- Documentation of the exception in code comments
- Remediation plan or timeline for bringing into compliance

**Version**: 1.0.0 | **Ratified**: 2025-01-24 | **Last Amended**: 2025-01-24