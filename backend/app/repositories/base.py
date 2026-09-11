from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: str) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def filter_by(self, **kwargs) -> List[ModelType]:
        return self.db.query(self.model).filter_by(**kwargs).all()

    def first_by(self, **kwargs) -> Optional[ModelType]:
        return self.db.query(self.model).filter_by(**kwargs).first()

    def create(self, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], BaseModel]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> Optional[ModelType]:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj

    def count(self, **kwargs) -> int:
        query = self.db.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.count()
