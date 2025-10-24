# Quickstart Guide: Starter Web Application

**Goal**: Get the full application running locally in under 10 minutes

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Python | 3.11+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | Frontend build tool | [nodejs.org](https://nodejs.org/) |
| Docker | 24+ | Containerization (optional) | [docker.com](https://www.docker.com/get-started) |
| Git | 2.30+ | Version control | [git-scm.com](https://git-scm.com/) |

**Verify installations**:
```bash
python --version    # Should show 3.11 or higher
node --version      # Should show v18.0.0 or higher
docker --version    # Should show 24.0 or higher (if using Docker)
```

## Quick Start (Docker - Recommended)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd school-match-ai

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

This will start:
- **Backend API** on http://localhost:8000
- **Frontend App** on http://localhost:5173
- **API Documentation** on http://localhost:8000/docs

### 3. Verify Installation

Open your browser and visit:
- http://localhost:5173 - Frontend application
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/health - Health check endpoint

### 4. Test Authentication Flow

1. **Register a new account**:
   - Go to http://localhost:5173/register
   - Email: `test@example.com`
   - Password: `Password123!`
   - Full Name: `Test User`

2. **Login**:
   - Go to http://localhost:5173/login
   - Use the credentials you just created

3. **View Profile**:
   - After login, you'll see your profile dashboard
   - Try updating your profile name

✅ **Success!** You now have a fully functional application running locally.

---

## Manual Setup (Without Docker)

### Backend Setup

#### 1. Navigate to Backend Directory

```bash
cd backend
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Install production and development dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

#### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file (optional - defaults work for local development)
# DATABASE_URL=sqlite+aiosqlite:///./app.db
# SECRET_KEY=your-secret-key-here
```

#### 5. Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Optional: Seed development data
python -m src.scripts.seed_dev_data
```

#### 6. Start Backend Server

```bash
# Development server with auto-reload
uvicorn src.main:app --reload --port 8000

# Or use make command
make dev
```

The backend will be running at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
# Open a new terminal window
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file (optional - defaults work for local development)
# VITE_API_BASE_URL=http://localhost:8000
```

#### 4. Start Frontend Development Server

```bash
# Development server with hot-reload
npm run dev

# Or use make command
make dev
```

The frontend will be running at: http://localhost:5173

---

## Project Structure Overview

```
school-match-ai/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── domains/           # Business domains (auth, user)
│   │   ├── shared/            # Shared utilities
│   │   ├── main.py            # App entry point
│   │   └── database.py        # Database configuration
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend configuration
│
├── frontend/                   # Vue.js frontend
│   ├── src/
│   │   ├── domains/           # Business domains (auth, user)
│   │   ├── stores/            # Pinia state stores
│   │   ├── router/            # Vue Router config
│   │   └── main.ts            # App entry point
│   ├── tests/                 # Frontend tests
│   ├── package.json           # Node dependencies
│   └── .env                   # Frontend configuration
│
└── docker-compose.yml         # Docker orchestration
```

## Common Development Tasks

### Backend Tasks

```bash
# Run tests
pytest                              # All tests
pytest tests/unit                   # Unit tests only
pytest tests/integration            # Integration tests only
pytest -v --cov=src                 # With coverage

# Code quality
black src/ tests/                   # Format code
isort src/ tests/                   # Sort imports
flake8 src/ tests/                  # Lint code
mypy src/                           # Type checking

# Database migrations
alembic revision --autogenerate -m "Add new field"    # Create migration
alembic upgrade head                                   # Apply migrations
alembic downgrade -1                                   # Rollback one migration
alembic history                                        # View migration history

# Start server
uvicorn src.main:app --reload                         # Development mode
uvicorn src.main:app --host 0.0.0.0 --port 8000       # Production mode
```

### Frontend Tasks

```bash
# Run tests
npm run test                        # Unit tests (Vitest)
npm run test:watch                  # Watch mode
npm run test:e2e                    # E2E tests (Playwright)
npm run test:e2e:ui                 # E2E with UI

# Code quality
npm run lint                        # ESLint check
npm run lint:fix                    # Auto-fix issues
npm run format                      # Prettier format

# Development
npm run dev                         # Start dev server
npm run build                       # Production build
npm run preview                     # Preview production build

# Type checking
npm run type-check                  # TypeScript validation
```

### Docker Tasks

```bash
# Development
docker-compose up                   # Start all services
docker-compose down                 # Stop all services
docker-compose logs -f backend      # View backend logs
docker-compose logs -f frontend     # View frontend logs
docker-compose restart backend      # Restart backend only

# Production
docker-compose -f docker-compose.prod.yml up --build
docker-compose -f docker-compose.prod.yml down

# Cleanup
docker-compose down -v              # Remove volumes
docker system prune -a              # Clean up Docker
```

## Adding a New Feature

Follow the constitution's workflow for adding features:

### 1. Define the Domain

Determine if your feature belongs in an existing domain or needs a new one:
- **Auth domain**: Authentication, authorization, sessions
- **User domain**: User profiles, preferences, settings
- **New domain**: If it doesn't fit existing domains, create a new one

### 2. Design API Contract

Create Pydantic schemas for your API:

```python
# backend/src/domains/example/schemas.py
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str
    description: str

class ExampleResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
```

### 3. Write Tests First (TDD)

```python
# backend/tests/unit/test_example_service.py
async def test_create_example():
    service = ExampleService(db)
    result = await service.create(name="Test", description="Test description")
    assert result.name == "Test"
```

### 4. Implement Backend (Bottom-Up)

**Repository** (data access):
```python
# backend/src/domains/example/repository.py
class ExampleRepository(BaseRepository):
    async def create(self, data: ExampleCreate) -> Example:
        # Database operations
```

**Service** (business logic):
```python
# backend/src/domains/example/service.py
class ExampleService:
    def __init__(self, repo: ExampleRepository):
        self.repo = repo
    
    async def create_example(self, data: ExampleCreate) -> Example:
        # Business logic
```

**Router** (HTTP handlers):
```python
# backend/src/domains/example/router.py
@router.post("/examples", response_model=ExampleResponse)
async def create_example(
    data: ExampleCreate,
    service: ExampleService = Depends(get_example_service)
):
    return await service.create_example(data)
```

### 5. Implement Frontend (Top-Down)

**Types**:
```typescript
// frontend/src/domains/example/types/example.types.ts
export interface Example {
  id: number
  name: string
  description: string
  createdAt: string
}
```

**Service** (API calls):
```typescript
// frontend/src/domains/example/services/exampleService.ts
export const exampleService = {
  async create(data: ExampleCreate): Promise<Example> {
    const response = await api.post('/examples', data)
    return response.data
  }
}
```

**Composable** (logic):
```typescript
// frontend/src/domains/example/composables/useExample.ts
export function useExample() {
  const example = ref<Example | null>(null)
  
  const create = async (data: ExampleCreate) => {
    example.value = await exampleService.create(data)
  }
  
  return { example, create }
}
```

**Component** (UI):
```vue
<!-- frontend/src/domains/example/components/ExampleForm.vue -->
<script setup lang="ts">
import { useExample } from '../composables/useExample'

const { create } = useExample()

const submit = async () => {
  await create({ name: '...', description: '...' })
}
</script>

<template>
  <form @submit.prevent="submit">
    <!-- Form fields -->
  </form>
</template>
```

## Testing Your Application

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run specific test
pytest tests/unit/test_auth_service.py::test_register_user

# Run tests matching pattern
pytest -k "auth"
```

### Frontend Testing

```bash
# Unit tests (Vitest)
npm run test

# Component tests with UI
npm run test:ui

# E2E tests (Playwright)
npm run test:e2e

# E2E tests with UI
npm run test:e2e:ui

# E2E tests in specific browser
npm run test:e2e -- --project=chromium
```

## Troubleshooting

### Backend Issues

**Database errors**:
```bash
# Reset database
rm app.db
alembic upgrade head

# Check database connections
python -c "from src.database import engine; print(engine)"
```

**Import errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate    # Windows

# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

**Port conflicts**:
```bash
# Check if port 8000 is in use
lsof -i :8000           # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn src.main:app --reload --port 8001
```

### Frontend Issues

**Build errors**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

**API connection errors**:
```bash
# Check API base URL in .env
cat frontend/.env

# Ensure backend is running
curl http://localhost:8000/health
```

**Hot reload not working**:
```bash
# Restart dev server
npm run dev

# Check Vite config
cat vite.config.ts
```

### Docker Issues

**Container won't start**:
```bash
# View container logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Volume permission issues**:
```bash
# On Linux, fix permissions
sudo chown -R $USER:$USER .
```

## Next Steps

Now that you have the application running:

1. **Explore the API**: Visit http://localhost:8000/docs to see all endpoints
2. **Read the Constitution**: Review `.specify/memory/constitution.md` for development principles
3. **Review the Data Model**: Check `specs/001-starter-app-structure/data-model.md`
4. **Add Your First Feature**: Follow the workflow above to add new functionality
5. **Run Tests**: Ensure everything works with `pytest` and `npm test`
6. **Customize**: Update branding, colors, and content to match your project

## Getting Help

- **Documentation**: Check `specs/001-starter-app-structure/` for detailed docs
- **API Reference**: http://localhost:8000/docs (when running)
- **Constitution**: `.specify/memory/constitution.md` for development guidelines
- **Issues**: Report bugs or ask questions in the repository issues

---

**Estimated Time to First Working App**: 10 minutes  
**Time to First Feature**: 30 minutes  
**Time to Full Productivity**: 1-2 hours

Happy coding! 🚀

