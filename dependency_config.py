from database_config import SessionLocal, Base, engine

# Dependencia para la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    Base.metadata.create_all(bind=engine)

