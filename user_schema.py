from typing import Optional
from pydantic import BaseModel, Field

from user_role import UserRoleEnum

class UserSchema(BaseModel):
     name: str
     lastname: str
     email: str
     institution_name: str
     profile_picture: Optional[str] 
     role: Optional[UserRoleEnum]

class UpdateUserSchema(BaseModel):
    name: Optional[str]
    lastname: Optional[str]
    profile_picture: Optional[str]