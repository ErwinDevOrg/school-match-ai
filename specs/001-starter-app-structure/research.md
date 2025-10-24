# Research: Starter Web Application Structure

**Feature**: 001-starter-app-structure  
**Date**: October 24, 2025  
**Purpose**: Document technology decisions, best practices, and patterns for the starter application

## Technology Stack Decisions

### Backend Framework: FastAPI

**Decision**: Use FastAPI 0.104+ as the backend framework

**Rationale**:
- Modern async/await support for high performance (required by constitution)
- Automatic OpenAPI/Swagger documentation (FR-019, Gate 3: API Contract First)
- Built-in Pydantic validation for type safety (Gate 5: Type Safety)
- Excellent developer experience with automatic interactive docs
- Strong ecosystem support for JWT, CORS, database integration
- Aligns perfectly with constitution requirements

**Alternatives Considered**:
- **Django**: Rejected - Too heavyweight for starter template, synchronous by default, violates constitution's "No Django" constraint
- **Flask**: Rejected - Lacks built-in async support, manual OpenAPI setup, violates constitution constraint
- **Node.js/Express**: Rejected - Specification requires Python backend

**Best Practices**:
- Use async route handlers for all database operations
- Leverage dependency injection for database sessions and authentication
- Structure responses with Pydantic models for automatic validation
- Enable CORS middleware with explicit origin configuration

### Frontend Framework: Vue 3 Composition API

**Decision**: Use Vue 3.3+ with Composition API and TypeScript

**Rationale**:
- Specification explicitly requires Vue.js frontend
- Composition API provides better TypeScript support and code reusability
- Aligns with constitution requirement (no Options API)
- Reactive system well-suited for authentication state management
- Excellent developer experience with Vue DevTools

**Alternatives Considered**:
- **Vue 2**: Rejected - End of life, lacks Composition API, poor TypeScript support
- **Vue 3 Options API**: Rejected - Violates constitution's "No Options API" constraint
- **React/Angular**: Rejected - Specification requires Vue.js

**Best Practices**:
- Use `<script setup>` syntax for cleaner, more concise components
- Leverage composables for shared logic (useAuth, useUser)
- Implement proper TypeScript types for all props and emits
- Use Vue Router for navigation with route guards for authentication

### Database: SQLite with SQLAlchemy ORM

**Decision**: Use SQLite for local development with SQLAlchemy 2.0+ ORM

**Rationale**:
- Zero-config setup (SC-001: 10-minute setup requirement)
- Cross-platform compatibility (SC-004: Windows, macOS, Linux)
- SQLAlchemy provides production-ready patterns that work with PostgreSQL migration path
- Constitution allows SQLite for local development
- File-based database simplifies containerization

**Alternatives Considered**:
- **PostgreSQL only**: Rejected - Requires Docker/installation, violates zero-config requirement for quick start
- **MongoDB**: Rejected - Clarification session specified relational database with SQLAlchemy
- **In-memory only**: Rejected - Data loss on restart, poor developer experience

**Best Practices**:
- Use SQLAlchemy 2.0 async patterns with AsyncSession
- Write Alembic migrations compatible with both SQLite and PostgreSQL
- Avoid database-specific features for migration flexibility
- Use proper indexes on foreign keys and frequently queried columns
- Implement soft deletes for user records

### Authentication: JWT with Access/Refresh Tokens

**Decision**: Implement JWT-based authentication with separate access and refresh tokens

**Rationale**:
- Clarification session specified JWT over session-based auth
- Stateless design aligns with constitution (Gate 7: State Management)
- Industry standard for API authentication
- Works well with separate frontend/backend architecture
- Enables horizontal scaling without session storage

**Alternatives Considered**:
- **Session-based**: Rejected - Requires stateful backend, doesn't scale horizontally
- **OAuth2 third-party only**: Rejected - Adds external dependencies, more complex for starter
- **Single token only**: Rejected - Security risk with long-lived tokens, no revocation strategy

**Best Practices**:
- Access tokens: Short-lived (15 minutes), include user ID and permissions
- Refresh tokens: Long-lived (7 days), stored securely, rotated on use
- Use bcrypt for password hashing (constitution requirement)
- Implement token blacklist for logout functionality
- Store refresh tokens in httpOnly cookies for web clients

### State Management: Pinia

**Decision**: Use Pinia 2.1+ for global state management

**Rationale**:
- Clarification session selected Pinia over Vuex
- Official Vue 3 state management solution
- Simpler API than Vuex, better TypeScript support
- Constitution requires Pinia (not Vuex)
- Perfect for auth state, user profile, and shared application state

**Alternatives Considered**:
- **Vuex**: Rejected - Verbos API, constitution explicitly requires Pinia
- **Component-only state**: Rejected - Insufficient for authentication state sharing
- **Composables with reactive**: Rejected - No devtools support, harder to debug

**Best Practices**:
- Create separate stores per domain (auth, user)
- Use actions for async operations (API calls)
- Persist auth tokens in localStorage via plugin
- Implement store reset on logout
- Use getters for computed derived state

### Build Tool: Vite

**Decision**: Use Vite 5.0+ as the frontend build tool

**Rationale**:
- Constitution specifies Vite as build tool
- Lightning-fast HMR (SC-002: < 2s reload requirement)
- Excellent TypeScript support out of the box
- Optimized production builds with automatic code splitting
- Official Vue 3 recommendation

**Alternatives Considered**:
- **Webpack**: Rejected - Slower HMR, more complex configuration
- **Parcel**: Rejected - Less ecosystem support, not officially recommended by Vue

**Best Practices**:
- Enable code splitting by route for optimal loading
- Configure proper environment variable handling
- Use Vite plugins for automatic component imports
- Optimize build for production with tree-shaking

### Testing Stack

**Decision**: pytest + pytest-asyncio (backend), Vitest + Playwright (frontend)

**Rationale**:
- Constitution specifies these exact tools
- pytest: Industry standard for Python, excellent async support
- Vitest: Vite-native testing, fast, compatible API with Jest
- Playwright: Cross-browser E2E testing, reliable, modern API
- Enables TDD workflow required by constitution (Gate 4)

**Alternatives Considered**:
- **unittest**: Rejected - Verbose API, less community support
- **Jest**: Rejected - Slower than Vitest for Vite projects
- **Cypress**: Rejected - Heavier, Playwright offers better API

**Best Practices**:
- Backend: Test services (unit), repositories (integration), routes (E2E)
- Frontend: Test composables (unit), components (integration), flows (E2E)
- Use fixtures for database setup/teardown
- Mock external APIs in unit tests
- Run E2E tests against real backend in CI/CD

### Containerization: Docker + Docker Compose

**Decision**: Use Docker for containerization with docker-compose for orchestration

**Rationale**:
- FR-018 requires containerization setup
- Constitution requires Docker + docker-compose
- Ensures environment parity (development mirrors production)
- Simplifies deployment to any Docker-compatible host
- Enables easy multi-service development (backend + frontend + database)

**Alternatives Considered**:
- **No containers**: Rejected - Violates FR-018 and constitution
- **Kubernetes**: Rejected - Overkill for starter, out of scope (explicit exclusion)
- **Podman**: Rejected - Less ecosystem support, not constitution-compliant

**Best Practices**:
- Multi-stage builds for optimized production images
- Non-root user in containers for security
- Health checks for both services
- Volume mounts for development hot-reload
- Separate docker-compose files for dev and production

## Development Patterns

### Error Handling Pattern

**Pattern**: Structured exceptions with consistent error responses

**Implementation**:
```python
# Backend: Custom exception hierarchy
class AppException(Exception):
    """Base exception with error code and message"""
    
class AuthenticationError(AppException):
    """401 - Invalid credentials"""
    
class AuthorizationError(AppException):
    """403 - Insufficient permissions"""

# FastAPI exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": str(exc)}
    )
```

```typescript
// Frontend: Axios interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    // Log technical details
    console.error('[API Error]', error)
    
    // Show user-friendly message
    const message = error.response?.data?.message || 'An error occurred'
    useToast().error(message)
    
    // Handle auth errors
    if (error.response?.status === 401) {
      useAuthStore().logout()
      router.push('/login')
    }
    
    return Promise.reject(error)
  }
)
```

**Rationale**: Satisfies Gate 6 (Fail Fast and Loud) and FR-011 (error handling pattern). Provides consistent error format across all endpoints, enables proper frontend error display, and centralizes error handling logic.

### Repository Pattern

**Pattern**: Data access layer abstraction

**Implementation**:
```python
# Base repository with common CRUD operations
class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, model, id: int):
        result = await self.session.execute(
            select(model).where(model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, instance):
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

# Domain-specific repository
class UserRepository(BaseRepository):
    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

**Rationale**: Satisfies Gate 2 (Separation of Concerns) and Gate 1 (Domain-Driven Design). Keeps database queries out of services, enables easy testing with mock repositories, and provides consistent data access patterns.

### Composable Pattern (Frontend)

**Pattern**: Reusable stateful logic

**Implementation**:
```typescript
// useAuth.ts - Authentication composable
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  
  const login = async (email: string, password: string) => {
    try {
      await authStore.login(email, password)
      router.push('/dashboard')
    } catch (error) {
      // Error already handled by interceptor
      throw error
    }
  }
  
  const logout = async () => {
    await authStore.logout()
    router.push('/login')
  }
  
  return {
    isAuthenticated: computed(() => authStore.isAuthenticated),
    user: computed(() => authStore.user),
    login,
    logout
  }
}
```

**Rationale**: Satisfies Gate 7 (State Management Discipline) and constitution's component structure requirements. Separates business logic from UI components, enables reusability, and provides clear testing boundaries.

### Dependency Injection Pattern (Backend)

**Pattern**: FastAPI dependencies for cross-cutting concerns

**Implementation**:
```python
# Get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Get current authenticated user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Verify JWT token
    payload = jwt.decode(token, SECRET_KEY)
    user_id = payload.get("sub")
    
    # Load user from database
    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise AuthenticationError("Invalid token")
    return user

# Use in routes
@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

**Rationale**: Follows FastAPI best practices, enables clean route handlers, centralizes authentication logic, and makes testing easier through dependency overrides.

## Code Quality & Tooling

### Linting & Formatting

**Backend**:
- **Black**: Python code formatter (opinionated, zero-config)
- **isort**: Import sorting
- **flake8**: Style guide enforcement
- **mypy**: Static type checking

**Frontend**:
- **ESLint**: JavaScript/TypeScript linting with Vue plugin
- **Prettier**: Code formatting
- **typescript-eslint**: TypeScript-specific rules

**Pre-commit Hooks**:
- Run formatters and linters before each commit (FR-014)
- Prevent commits with type errors or linting issues
- Fast feedback loop for code quality

### API Documentation

**OpenAPI/Swagger UI**:
- Automatically generated from Pydantic schemas (FR-019)
- Available at `/docs` endpoint
- Interactive testing interface
- Request/response examples
- Authentication testing support

**TypeScript Type Generation**:
- Generate frontend types from OpenAPI schema
- Keep frontend/backend contracts synchronized
- Catch breaking changes at compile time

## Development Workflow

### Adding a New Feature (Following Constitution)

1. **Define Domain**: Determine if it fits in auth/user or needs new domain
2. **Design API Contract**: Create Pydantic schemas, update OpenAPI
3. **Write Tests First** (TDD):
   - Backend service tests (business logic)
   - Repository tests (data access)
   - Router integration tests (API endpoints)
   - Frontend composable tests (logic)
   - Component tests (UI behavior)
4. **Implement Backend** (order matters):
   - Repository layer (data access)
   - Service layer (business logic)
   - Router layer (HTTP handlers)
5. **Implement Frontend**:
   - TypeScript types (from OpenAPI)
   - API service (HTTP calls)
   - Composable (state + logic)
   - Components/Views (UI)
6. **E2E Testing**: Full user journey test
7. **Code Review**: Verify constitution compliance

### Environment Configuration

**Backend (.env)**:
```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Frontend (.env)**:
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Environment
VITE_ENVIRONMENT=development
```

### Common Development Commands

**Backend**:
```bash
# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Run linters
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

**Frontend**:
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm run test          # Unit tests
npm run test:e2e      # E2E tests

# Run linters
npm run lint
npm run format

# Build for production
npm run build
```

**Docker**:
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up

# Rebuild after dependency changes
docker-compose build
```

## Security Considerations

### Authentication Security

- **Password Storage**: bcrypt with salt (min 12 rounds)
- **Token Storage**: 
  - Access token: Memory (store state) or sessionStorage
  - Refresh token: httpOnly cookie or secure localStorage
- **Token Expiration**: Short-lived access (15 min), long-lived refresh (7 days)
- **Token Rotation**: Rotate refresh token on each use
- **Logout**: Invalidate tokens on server-side blacklist

### API Security

- **CORS**: Explicit origin whitelist, no wildcard in production
- **Rate Limiting**: 5 requests/minute on auth endpoints
- **Input Validation**: Pydantic validates all inputs at API boundary
- **SQL Injection**: SQLAlchemy ORM (no raw SQL)
- **XSS Prevention**: Vue automatic escaping, sanitize v-html
- **HTTPS Only**: Force HTTPS in production
- **Security Headers**: HSTS, X-Content-Type-Options, X-Frame-Options

### Data Protection

- **Sensitive Data**: Never log passwords, tokens, or PII
- **Database**: Use parameterized queries via ORM
- **Environment Variables**: Never commit .env files
- **Secrets**: Use environment variables, rotate regularly

## Performance Optimization

### Backend Performance

- **Async Operations**: All database and I/O operations use async/await
- **Database Indexes**: Index on email, created_at, foreign keys
- **Connection Pooling**: SQLAlchemy pool size 20, overflow 0
- **Query Optimization**: Use select_related to avoid N+1 queries
- **Response Compression**: Gzip middleware enabled

### Frontend Performance

- **Code Splitting**: Automatic route-based splitting with Vite
- **Lazy Loading**: Components and routes loaded on demand
- **Asset Optimization**: Image compression, tree-shaking
- **Caching**: Service worker for static assets (optional)
- **Bundle Analysis**: Use rollup-plugin-visualizer to monitor size

## Migration Path to Production

### Database Migration (SQLite → PostgreSQL)

1. Update DATABASE_URL in environment variables
2. Run same Alembic migrations (compatible with both)
3. Migrate data if needed (export/import or pg_dump equivalent)
4. Test application thoroughly against PostgreSQL

### Scaling Considerations

- **Horizontal Scaling**: Stateless backend supports load balancing
- **Database**: Move to PostgreSQL for production features
- **File Storage**: Replace local storage with S3/CloudFlare
- **Sessions**: Add Redis for token blacklist if needed
- **Monitoring**: Add Sentry/DataDog for production observability

### Deployment Options

- **Docker**: Deploy containers to any Docker host
- **Cloud Run**: Serverless container deployment
- **Heroku**: Quick deployment with PostgreSQL addon
- **VPS**: Traditional server deployment (DigitalOcean, Linode)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Security Guidelines](https://owasp.org/www-project-web-security-testing-guide/)

---

**Status**: Research complete. All NEEDS CLARIFICATION items resolved. Proceed to Phase 1 (Design).

