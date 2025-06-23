"""
database/manager.py
Dynamic, config-driven multi-table async database manager for PostgreSQL.
"""

import asyncio
from typing import Dict, Any, List, Type, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, JSON, Integer, DateTime, Boolean
from sqlalchemy.exc import NoResultFound
from sqlalchemy.inspection import inspect
from .exceptions import DatabaseError, RecordNotFoundError
from .metrics import record_db_operation
from .utils import log_info

# Base for dynamic models
DynamicBase = declarative_base()

class DatabaseManager:
    """
    Dynamic multi-table async database manager with config-driven table definitions.
    """
    def __init__(self, db_url: str, config_manager):
        self._engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600
        )
        self._SessionLocal = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        self._lock = asyncio.Lock()
        self._models: Dict[str, Type] = {}
        self._config_manager = config_manager
        self._type_map = {
            "string": String,
            "json": JSON,
            "integer": Integer,
            "datetime": DateTime,
            "boolean": Boolean
        }

    async def setup(self):
        """
        Async setup: create tables from config and initialize models.
        """
        config = await self._config_manager.get()
        table_defs = getattr(config.database, "tables", [])
        
        # Generate models for each table definition
        for table_def in table_defs:
            model = self._create_model(table_def)
            self._models[table_def["name"]] = model
        
        # Create tables in database
        async with self._engine.begin() as conn:
            for model in self._models.values():
                await conn.run_sync(model.metadata.create_all)
        
        log_info("DatabaseManager: Dynamic table setup complete")

    def _create_model(self, table_def: dict) -> Type:
        """
        Dynamically create SQLAlchemy model from table definition.
        """
        attrs = {"__tablename__": table_def["name"]}
        
        # Add columns based on field definitions
        for field_name, field_type in table_def.get("fields", {}).items():
            col_type = self._type_map.get(field_type.lower())
            if not col_type:
                raise DatabaseError(f"Unsupported field type: {field_type}")
            
            # Set primary key if field name is 'id'
            if field_name == "id":
                attrs[field_name] = Column(col_type, primary_key=True)
            else:
                attrs[field_name] = Column(col_type)
        
        # Create model class
        return type(table_def["name"].capitalize(), (DynamicBase,), attrs)

    async def shutdown(self):
        """Graceful shutdown"""
        await self._engine.dispose()
        log_info("DatabaseManager: Shutdown complete")

    def get_model(self, table_name: str) -> Type:
        """Get model class for table"""
        if table_name not in self._models:
            raise DatabaseError(f"Table '{table_name}' not configured")
        return self._models[table_name]

    async def create_record(self, table_name: str,  dict) -> dict:
        """
        Create a new record in specified table.
        """
        model = self.get_model(table_name)
        async with self._lock, self._SessionLocal() as session:
            try:
                db_rec = model(**data)
                session.add(db_rec)
                await session.commit()
                await session.refresh(db_rec)
                record_db_operation("create")
                return self._model_to_dict(db_rec)
            except Exception as e:
                await session.rollback()
                raise DatabaseError(f"Create failed: {str(e)}")

    async def get_record(self, table_name: str, record_id: Any) -> dict:
        """
        Get record by primary key.
        """
        model = self.get_model(table_name)
        async with self._lock, self._SessionLocal() as session:
            try:
                db_rec = await session.get(model, record_id)
                if not db_rec:
                    raise RecordNotFoundError(f"Record {record_id} not found")
                record_db_operation("get")
                return self._model_to_dict(db_rec)
            except Exception as e:
                raise DatabaseError(f"Get failed: {str(e)}")

    async def update_record(self, table_name: str, record_id: Any,  dict) -> dict:
        """
        Update record by primary key.
        """
        model = self.get_model(table_name)
        async with self._lock, self._SessionLocal() as session:
            try:
                db_rec = await session.get(model, record_id)
                if not db_rec:
                    raise RecordNotFoundError(f"Record {record_id} not found")
                
                for key, value in data.items():
                    setattr(db_rec, key, value)
                
                await session.commit()
                await session.refresh(db_rec)
                record_db_operation("update")
                return self._model_to_dict(db_rec)
            except Exception as e:
                await session.rollback()
                raise DatabaseError(f"Update failed: {str(e)}")

    async def delete_record(self, table_name: str, record_id: Any) -> None:
        """
        Delete record by primary key.
        """
        model = self.get_model(table_name)
        async with self._lock, self._SessionLocal() as session:
            try:
                db_rec = await session.get(model, record_id)
                if not db_rec:
                    raise RecordNotFoundError(f"Record {record_id} not found")
                
                await session.delete(db_rec)
                await session.commit()
                record_db_operation("delete")
            except Exception as e:
                await session.rollback()
                raise DatabaseError(f"Delete failed: {str(e)}")

    async def query_records(self, table_name: str, filters: dict = None, limit: int = 100) -> List[dict]:
        """
        Query records with optional filters.
        """
        model = self.get_model(table_name)
        async with self._lock, self._SessionLocal() as session:
            try:
                query = session.query(model)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(model, key):
                            query = query.filter(getattr(model, key) == value)
                
                # Execute query
                result = await session.execute(query.limit(limit))
                records = result.scalars().all()
                record_db_operation("query")
                return [self._model_to_dict(rec) for rec in records]
            except Exception as e:
                raise DatabaseError(f"Query failed: {str(e)}")

    def _model_to_dict(self, model_instance) -> dict:
        """Convert model instance to dictionary"""
        return {c.key: getattr(model_instance, c.key) for c in inspect(model_instance).mapper.column_attrs}
