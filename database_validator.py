from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from error_factory import DatabaseError

class ValidatorDatabase:

    @staticmethod
    def handle_error(exception: Exception, operation: str, model_class: str, item_id  = None, attribute: str = None, value = None):
        """
        Handles various types of database errors and raises appropriate exceptions.
        """
        if isinstance(exception, IntegrityError):
            raise DatabaseError(f"Integrity error during {operation} for {model_class} ({item_id if item_id else ''}): {str(exception)}", code=400)
        elif isinstance(exception, NoResultFound):
            raise DatabaseError(f"{model_class} not found.", code=404)
        elif isinstance(exception, SQLAlchemyError):
            raise DatabaseError(f"Database error during {operation} for {model_class} ({item_id if item_id else ''}): {str(exception)}", code=400)
        else:
            raise DatabaseError(f"Unexpected error during {operation} for {model_class} ({item_id if item_id else ''}): {str(exception)}", code=500)

    @staticmethod
    def check_not_found(result, model_class: str, item_id: int = None, attribute: str = None, value = None):
        """
        Checks if the result is None or not found, and raises a NoResultFound exception with a message.
        """
        if result is None:
            if item_id:
                raise NoResultFound(f"{model_class} with ID {item_id} not found.")
            elif attribute and value:
                raise NoResultFound(f"No {model_class} found with {attribute}={value}")
            else:
                raise NoResultFound(f"{model_class} not found.")
