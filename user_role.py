from enum import Enum

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
