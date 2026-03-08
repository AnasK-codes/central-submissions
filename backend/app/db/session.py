from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create the engine using the URL from your .env file
engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# 2. Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()