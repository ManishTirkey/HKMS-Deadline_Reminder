from sqlalchemy import create_engine, Column, BigInteger, Text, DateTime, func, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Create base class for models
Base = declarative_base()


# Define models
class HKMSServiceCategory(Base):
    __tablename__ = "hkms_service_category"
    # id = Column(BigInteger, primary_key=True, autoincrement=True) # for postgresql
    id = Column(Integer, primary_key=True, autoincrement=True)  # for sqlLite
    category_name = Column(Text, unique=True, nullable=False)
    created_by = Column(Text, default='system', nullable=False)
    updated_by = Column(Text, default='system', nullable=False)
    created_dt = Column(DateTime, default=func.now(), nullable=False)
    updated_dt = Column(DateTime, default=func.now(), nullable=False)


# Engine and session will be created when needed
engine = None
SessionLocal = None


def get_engine():
    """Get or create the database engine with schema configuration"""
    global engine
    
    try: 
        if engine is None:
            from app.config import settings

            # Create the engine
            engine = create_engine(settings.database_url)

            # If it's a PostgreSQL database, set the schema
            if 'postgresql' in settings.database_url.lower():
                try:
                    with engine.connect() as conn:
                        # Create schema if it doesn't exist
                        conn.execute(text("CREATE SCHEMA IF NOT EXISTS hkms"))
                        conn.commit()

                        # Set the search path to hkms schema
                        conn.execute(text("SET search_path TO hkms, public"))
                        conn.commit()
                        print("✅ PostgreSQL schema set to 'hkms'")

                except Exception as e:
                    print(f"⚠️  Warning: Could not set schema: {e}")

        return engine
    except Exception as e: 
        print(f"error found: {e}")


def get_sessionlocal():
    try:
        global SessionLocal
        if SessionLocal is None:
            engine = get_engine()
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal
    except Exception as e:
        print(f"error found: {e}")
