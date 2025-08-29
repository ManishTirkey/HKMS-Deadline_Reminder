from sqlalchemy.orm import Session
from app.models.database_models import Base, get_engine, get_sessionlocal, HKMSServiceCategory


def get_db():
    SessionLocal = get_sessionlocal()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create database tables"""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        return True, "Tables created successfully"
    except Exception as e:
        return False, f"Error creating tables: {str(e)}"


def insert_service(db: Session, category_name: str):
    """Insert a new service category if it doesn't exist"""

    try:
        exists = db.query(HKMSServiceCategory).filter(HKMSServiceCategory.category_name == category_name).first()
        if not exists:
            new_cat = HKMSServiceCategory(category_name=category_name)
            db.add(new_cat)
            db.commit()
    except Exception as e:
        print(f"error found: {e}")


def get_service_categories(db: Session):
    """Retrieve all service categories from the database"""
    try:
        return db.query(HKMSServiceCategory).all()

    except Exception as e:
        print(f"error found: {e}")

