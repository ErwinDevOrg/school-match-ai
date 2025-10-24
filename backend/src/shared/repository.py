"""
Base Repository Pattern

Provides generic CRUD operations for SQLAlchemy models with async support.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing generic CRUD operations
    
    Args:
        model: SQLAlchemy model class
        session: Async database session
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get a record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all records with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Create a new record
        
        Args:
            data: Dictionary of model attributes
            
        Returns:
            Created model instance
        """
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def update(
        self, 
        id: int, 
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update an existing record
        
        Args:
            id: Record ID
            data: Dictionary of attributes to update
            
        Returns:
            Updated model instance or None if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def delete(self, id: int) -> bool:
        """
        Delete a record by ID
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        await self.session.delete(instance)
        await self.session.commit()
        return True
    
    async def count(self) -> int:
        """
        Count total records
        
        Returns:
            Total number of records
        """
        result = await self.session.execute(
            select(self.model).count()
        )
        return result.scalar_one()

