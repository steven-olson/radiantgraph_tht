from src.data.database import engine, get_db, Base


def create_tables():
    Base.metadata.create_all(bind=engine)