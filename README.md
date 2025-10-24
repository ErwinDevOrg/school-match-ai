# School Match AI - Starter Web Application

A production-ready starter template built with **FastAPI** (backend) and **Vue 3** (frontend) following domain-driven design principles.

## 🚀 Quick Start

Get the full application running locally in under 10 minutes!

**Prerequisites**: Python 3.11+, Node.js 18+, Docker (optional)

```bash
# Clone and setup
git clone <repository-url>
cd school-match-ai

# Quick start with Docker (recommended)
docker-compose up --build

# Or manual setup (see below)
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

📖 **Detailed Setup**: See [quickstart.md](specs/001-starter-app-structure/quickstart.md)

## 📁 Project Structure

```
school-match-ai/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── domains/     # Business domains (auth, user)
│   │   ├── shared/      # Shared utilities
│   │   └── main.py      # App entry point
│   ├── tests/           # Backend tests
│   └── requirements.txt # Python dependencies
│
├── frontend/            # Vue 3 + TypeScript frontend
│   ├── src/
│   │   ├── domains/     # Business domains (auth, user)
│   │   ├── stores/      # Pinia state stores
│   │   └── main.ts      # App entry point
│   ├── tests/           # Frontend tests
│   └── package.json     # Node dependencies
│
├── specs/               # Feature specifications & documentation
└── docker-compose.yml   # Docker orchestration
```

## ✨ Features

- ✅ **JWT Authentication**: Secure login with access/refresh tokens
- ✅ **User Management**: Registration, profile, password management
- ✅ **Auto-generated API Docs**: Interactive Swagger UI
- ✅ **Hot Reload**: Backend & frontend auto-reload on changes
- ✅ **Type Safety**: Pydantic (backend) + TypeScript (frontend)
- ✅ **State Management**: Pinia stores for auth and user data
- ✅ **Testing**: Unit, integration, and E2E test examples
- ✅ **Code Quality**: Linters, formatters, pre-commit hooks
- ✅ **Docker**: Containerized for development and production
- ✅ **Domain-Driven Design**: Clear separation of concerns

## 🛠️ Tech Stack

**Backend**:
- FastAPI 0.104+ (async Python web framework)
- SQLAlchemy 2.0+ (async ORM)
- SQLite (dev) / PostgreSQL (production)
- Pydantic v2 (data validation)
- JWT authentication with bcrypt

**Frontend**:
- Vue 3.3+ with Composition API
- TypeScript 5.0+ (strict mode)
- Pinia 2.1+ (state management)
- Vite 5.0+ (build tool)
- Axios (HTTP client)

**Testing**:
- Backend: pytest + pytest-asyncio
- Frontend: Vitest + Playwright

**Code Quality**:
- Backend: black, isort, flake8, mypy
- Frontend: ESLint, Prettier, TypeScript

## 📖 Documentation

- **[Quickstart Guide](specs/001-starter-app-structure/quickstart.md)** - Get started in 10 minutes
- **[Feature Spec](specs/001-starter-app-structure/spec.md)** - Requirements and user stories
- **[Implementation Plan](specs/001-starter-app-structure/plan.md)** - Architecture and tech decisions
- **[Data Model](specs/001-starter-app-structure/data-model.md)** - Database schema
- **[API Contracts](specs/001-starter-app-structure/contracts/openapi.yaml)** - OpenAPI specification
- **[Task Breakdown](specs/001-starter-app-structure/tasks.md)** - 206 implementation tasks
- **[Constitution](.specify/memory/constitution.md)** - Development principles

## 🚦 Development

### Backend

```bash
cd backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Format and lint
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev

# Run tests
npm run test        # Unit tests
npm run test:e2e    # E2E tests

# Format and lint
npm run lint
npm run format
```

### Docker

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🧪 Testing

```bash
# Backend tests with coverage
cd backend
pytest --cov=src --cov-report=html

# Frontend unit tests
cd frontend
npm run test

# Frontend E2E tests
npm run test:e2e
```

## 📝 Adding a New Feature

Follow the constitution's workflow:

1. **Define Domain**: Determine which domain owns the feature
2. **Design API Contract**: Create Pydantic schemas
3. **Write Tests First**: TDD approach
4. **Implement Backend**: Repository → Service → Router
5. **Implement Frontend**: Types → Service → Composable → Component
6. **Integration Test**: E2E test for complete user journey

See [ADDING_FEATURES.md](docs/ADDING_FEATURES.md) for detailed guide.

## 🔒 Security

- Passwords hashed with bcrypt (12+ rounds)
- JWT tokens with short-lived access (15min) and refresh (7 days)
- CORS configured with explicit origins
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via Vue's automatic escaping
- Environment variables for all secrets
- Rate limiting on authentication endpoints

## 📦 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment instructions including:
- Docker deployment
- VPS deployment
- Cloud deployment (Heroku, Railway, etc.)
- Database migration (SQLite → PostgreSQL)

## 🤝 Contributing

1. Follow the [Constitution](.specify/memory/constitution.md) for development standards
2. Run pre-commit hooks: `pre-commit install`
3. Write tests for new features
4. Ensure all linters pass before committing
5. Follow domain-driven design principles

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with the speckit workflow for systematic feature development.

---

**Questions?** Check the [quickstart guide](specs/001-starter-app-structure/quickstart.md) or review the [documentation](specs/001-starter-app-structure/).

