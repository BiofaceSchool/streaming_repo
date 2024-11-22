from datetime import datetime
import uuid
from sqlalchemy import JSON, Column, String, Enum
from sqlalchemy.orm import relationship
from user_role import UserRoleEnum
from typing import Optional
from database_config import Base

class User(Base):
    __tablename__ = 'users'

    id: str = Column(String(length=36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()), unique=True)
    name: str = Column(String(length=100), nullable=False)
    lastname: str = Column(String(length=100) , nullable=False)
    email: str = Column(String(length=100), nullable=False, unique=True)
    password: str = Column(String(length=100), nullable=False)
    institution_name: str = Column(String(length=100), nullable=False)
    profile_picture: Optional[str] = Column(String(length=100), nullable=True)
    role: UserRoleEnum = Column(Enum(UserRoleEnum), default=UserRoleEnum.ADMIN)
    embeddings: Optional[list] = Column(JSON, nullable=True) 

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'institution_name': self.institution_name,
            'profile_picture': self.profile_picture,
            'role': self.role.value  # Asegúrate de obtener el valor del Enum si es necesario
        }

    class Config:
        from_attributes = True 