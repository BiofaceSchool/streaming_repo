from http import HTTPStatus
from fastapi import HTTPException

class CreateErrorFactory(HTTPException):
    
    def __init__(self, message, code=None):
        # Asigna el código de estado HTTP y el mensaje
        self.code = code if code is not None else 500  # Valor por defecto 500
        super().__init__(status_code=self.code, detail=message)  # Llama al constructor de HTTPException


class ValidationError(CreateErrorFactory):
    def __init__(self, message, code=None):
        prefixed_message = f"Validation Error: {message}"
        code= code if code is not None else HTTPStatus.BAD_REQUEST  # Valor por defecto 400
        super().__init__(prefixed_message, code)  # Llama al constructor de la clase base
    
class DatabaseError(CreateErrorFactory):
    def __init__(self, message, code=None):
        prefixed_message = f"Database Error: {message}"
        super().__init__(prefixed_message, code)  # Llama al constructor de la clase base

class ConnectionError(CreateErrorFactory):

    def __init__(self, message, code=None):
        prefixed_message = f"Connection Error: {message}"
        super().__init__(prefixed_message, code)  # Llama al constructor de la clase base
