# Data Model: Starter Web Application Structure

**Feature**: 001-starter-app-structure  
**Date**: October 24, 2025  
**Database**: SQLite (development), PostgreSQL-compatible via SQLAlchemy

## Overview

This document defines the database schema for the starter application. The model demonstrates authentication and user management patterns following domain-driven design principles. All models use SQLAlchemy 2.0 async patterns and are designed to work with both SQLite (development) and PostgreSQL (production).

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ email (UNIQUE)  │
│ hashed_password │
│ full_name       │
│ is_active       │
│ is_verified     │
│ created_at      │
│ updated_at      │
│ last_login_at   │
└─────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐
│  RefreshToken   │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ token           │
│ expires_at      │
│ revoked         │
│ created_at      │
└─────────────────┘
```

## Entities

### User

**Domain**: Auth  
**Purpose**: Represents authenticated users in the system  
**Table Name**: `users`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| email | String(255) | UNIQUE, NOT NULL, INDEX | User's email address (login credential) |
| hashed_password | String(255) | NOT NULL | bcrypt-hashed password (never store plain text) |
| full_name | String(100) | NOT NULL | User's display name |
| is_active | Boolean | NOT NULL, DEFAULT TRUE | Account active status (soft delete) |
| is_verified | Boolean | NOT NULL, DEFAULT FALSE | Email verification status |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Last modification timestamp |
| last_login_at | DateTime | NULLABLE | Most recent successful login |

#### Validation Rules

- **email**: 
  - Must be valid email format (validated by Pydantic EmailStr)
  - Case-insensitive uniqueness (stored lowercase)
  - Max length: 255 characters
- **hashed_password**: 
  - Never returned in API responses
  - Minimum 8 characters before hashing
  - bcrypt with 12+ rounds
- **full_name**: 
  - Min length: 2 characters
  - Max length: 100 characters
  - No special characters except spaces, hyphens, apostrophes
- **is_active**: 
  - FALSE for soft-deleted accounts
  - Prevents login when FALSE
- **is_verified**: 
  - Set to TRUE after email verification
  - Optional enforcement (configurable)

#### Relationships

- **refresh_tokens**: One-to-many relationship with RefreshToken (cascade delete)

#### Indexes

```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);
```

#### State Transitions

```
[Registration] → is_active=True, is_verified=False
     ↓
[Email Verification] → is_verified=True
     ↓
[Normal Use] → last_login_at updates on login
     ↓
[Deactivation] → is_active=False (soft delete)
     ↓
[Reactivation] → is_active=True (admin action)
```

#### Example SQLAlchemy Model

```python
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

---

### RefreshToken

**Domain**: Auth  
**Purpose**: Manages JWT refresh tokens for secure authentication  
**Table Name**: `refresh_tokens`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique token identifier |
| user_id | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Owner of this refresh token |
| token | String(500) | UNIQUE, NOT NULL, INDEX | JWT refresh token value |
| expires_at | DateTime | NOT NULL, INDEX | Token expiration timestamp |
| revoked | Boolean | NOT NULL, DEFAULT FALSE | Manual revocation flag |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Token issue timestamp |

#### Validation Rules

- **token**: 
  - Must be unique across all tokens
  - Cryptographically secure random string
  - Typically 200-400 characters (JWT format)
- **expires_at**: 
  - Must be future timestamp
  - Typically 7 days from creation
  - Cannot exceed maximum configured lifetime
- **revoked**: 
  - TRUE for manually invalidated tokens
  - Checked on every refresh attempt
- **user_id**: 
  - Must reference existing user
  - Cascade delete when user deleted

#### Relationships

- **user**: Many-to-one relationship with User

#### Indexes

```sql
CREATE UNIQUE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

#### State Transitions

```
[Token Creation] → revoked=False, expires_at set
     ↓
[Token Use] → If valid, create new token and revoke old one (rotation)
     ↓
[Manual Revocation] → revoked=True (logout, security event)
     ↓
[Expiration] → expires_at < NOW (automatic invalidation)
     ↓
[Cleanup] → Delete expired tokens older than 30 days (scheduled job)
```

#### Example SQLAlchemy Model

```python
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
    
    def is_valid(self) -> bool:
        """Check if token is still valid (not expired and not revoked)"""
        return not self.revoked and self.expires_at > datetime.utcnow()
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
```

---

## Database Initialization

### Alembic Migration Strategy

**Initial Migration** (001_initial_schema.py):
```python
"""Initial schema: users and refresh_tokens

Revision ID: 001
Create Date: 2025-10-24
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])

def downgrade():
    op.drop_table('refresh_tokens')
    op.drop_table('users')
```

### Seed Data (Development Only)

**Example Seed Script**:
```python
from datetime import datetime
from src.domains.auth.models import User
from src.shared.security import get_password_hash

async def seed_development_data(db: AsyncSession):
    """Create test users for development"""
    
    # Check if users already exist
    result = await db.execute(select(User).limit(1))
    if result.first():
        return  # Already seeded
    
    # Create demo users
    demo_users = [
        User(
            email="admin@example.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="Admin User",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        ),
        User(
            email="user@example.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        ),
    ]
    
    for user in demo_users:
        db.add(user)
    
    await db.commit()
    print(f"✅ Seeded {len(demo_users)} demo users")
```

## Data Access Patterns

### Common Queries

**1. Find User by Email**:
```python
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email.lower())
    )
    return result.scalar_one_or_none()
```

**2. Create User with Transaction**:
```python
async def create_user(db: AsyncSession, email: str, password: str, full_name: str) -> User:
    user = User(
        email=email.lower(),
        hashed_password=get_password_hash(password),
        full_name=full_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

**3. Get Valid Refresh Token**:
```python
async def get_valid_refresh_token(db: AsyncSession, token: str) -> RefreshToken | None:
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token == token)
        .where(RefreshToken.revoked == False)
        .where(RefreshToken.expires_at > datetime.utcnow())
    )
    return result.scalar_one_or_none()
```

**4. Revoke All User Tokens** (on password change):
```python
async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .values(revoked=True)
    )
    await db.commit()
```

**5. Cleanup Expired Tokens** (scheduled job):
```python
async def cleanup_expired_tokens(db: AsyncSession):
    cutoff = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        delete(RefreshToken)
        .where(RefreshToken.expires_at < cutoff)
    )
    await db.commit()
    return result.rowcount
```

## Data Migration Considerations

### SQLite → PostgreSQL Migration

The schema is designed to be compatible with both databases:

**Compatible Features**:
- Standard SQL types (Integer, String, Boolean, DateTime)
- Foreign key constraints
- Unique constraints
- Indexes

**Potential Issues & Solutions**:

| Issue | SQLite Behavior | PostgreSQL Behavior | Solution |
|-------|----------------|---------------------|----------|
| Boolean Type | Stored as 0/1 | Native boolean | Use SQLAlchemy Boolean type (handles both) |
| Datetime | TEXT or INTEGER | TIMESTAMP | Use SQLAlchemy DateTime (handles both) |
| Case Sensitivity | Case-insensitive LIKE | Case-sensitive LIKE | Use ILIKE in PostgreSQL, store email lowercase |
| Auto-increment | AUTOINCREMENT | SERIAL/IDENTITY | SQLAlchemy handles automatically |
| JSON Type | TEXT | JSONB | Use SQLAlchemy JSON type if needed later |

**Migration Script** (if moving existing data):
```bash
# Export from SQLite
sqlite3 app.db .dump > backup.sql

# Transform for PostgreSQL (manual or scripted)
# - Convert boolean values (0/1 → false/true)
# - Adjust datetime formats
# - Handle sequences

# Import to PostgreSQL
psql -U user -d database -f backup.sql
```

## Performance Considerations

### Query Optimization

**Indexed Queries** (fast):
- Lookup user by email: `O(log n)` via unique index
- Find refresh token: `O(log n)` via unique index
- Get user's tokens: `O(log n)` via foreign key index

**Expensive Queries** (avoid):
- Full table scans without WHERE clause
- LIKE queries without index prefix
- SELECT * (always specify columns)

### N+1 Query Prevention

**Bad** (N+1 queries):
```python
users = await db.execute(select(User))
for user in users:
    # Separate query for each user's tokens!
    tokens = user.refresh_tokens
```

**Good** (single query with join):
```python
users = await db.execute(
    select(User).options(selectinload(User.refresh_tokens))
)
```

### Connection Pool Settings

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Number of persistent connections
    max_overflow=0,         # No additional connections beyond pool
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False,             # Set True for query logging in dev
)
```

## Security Considerations

### Sensitive Data Handling

**Never Log or Return**:
- `hashed_password` field
- Raw `token` values in refresh_tokens
- Any password (even before hashing)

**Pydantic Schema Example** (excludes sensitive fields):
```python
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    # Exclude: hashed_password
    
    class Config:
        from_attributes = True
```

### Soft Delete Pattern

Instead of hard deletes, use `is_active=False`:
```python
async def deactivate_user(db: AsyncSession, user_id: int):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
```

Benefits:
- Preserves audit trail
- Enables account recovery
- Maintains referential integrity

## Testing Data

### Test Fixtures

```python
import pytest
from tests.factories import UserFactory, RefreshTokenFactory

@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    return await UserFactory.create(
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_verified=True
    )

@pytest.fixture
async def test_user_with_token(db_session, test_user):
    """Create a test user with valid refresh token"""
    token = await RefreshTokenFactory.create(
        user_id=test_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    return test_user, token
```

---

**Status**: Data model complete. Proceed to API contracts definition.

