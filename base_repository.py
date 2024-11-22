from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic, List

from database_validator import ValidatorDatabase

# Define a generic type T which should be a subclass of Base
T = TypeVar('T')  # Generic type

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class
        self.validator = ValidatorDatabase

    def add(self, item: T):
        try:
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.validator.handle_error(e, 'adding', self.model_class.__name__, item_id=item.id)

    def get_by_id(self, item_id: int):
        try:
            result = self.db.query(self.model_class).get(item_id)
            self.validator.check_not_found(result, self.model_class.__name__, item_id=item_id)
            return result
        except Exception as e:
            self.validator.handle_error(e, 'retrieving', self.model_class.__name__, item_id=item_id)

    def get_by_attribute(self, attribute: str, value):
        try:
            result = self.db.query(self.model_class).filter(getattr(self.model_class, attribute) == value).first()
            self.validator.check_not_found(result, self.model_class.__name__, attribute=attribute, value=value)  # Using check_not_found here
            return result
        except Exception as e:
            self.validator.handle_error(e, 'retrieving by attribute', self.model_class.__name__, attribute=attribute, value=value)

    def update(self, updated_item: T, item_id : int):
        try:
            item = self.db.query(self.model_class).get(item_id)

            self.validator.check_not_found(item, self.model_class.__name__, item_id=item_id) 

            for key, value in updated_item.dict().items():
                setattr(item, key, value)

            self.db.commit()
            return item
        except Exception as e:
            self.validator.handle_error(e, 'updating', self.model_class.__name__, item_id=item_id)

    def delete(self, item_id: int):
        try:
            item = self.db.query(self.model_class).get(item_id)

            self.validator.check_not_found(item, self.model_class.__name__, item_id=item_id)  # Using check_not_found here

            self.db.delete(item)
            self.db.commit()

            return item
        except Exception as e:
            self.validator.handle_error(e, 'deleting', self.model_class.__name__, item_id=item_id)

    def get_all(self):
        try:
            return self.db.query(self.model_class).all()
        except Exception as e:
            self.validator.handle_error(e, 'retrieving all', self.model_class.__name__)
