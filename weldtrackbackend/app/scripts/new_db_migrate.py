import subprocess
import sys

from sqlalchemy import create_engine

from app.core.config import settings
from app.db import Base
import app.models  # noqa: F401

db_url = settings.DATABASE_URL
if not db_url:
    print("Error: DATABASE_URL not found in settings.")
    sys.exit(1)

print("Building database tables...")
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

print("Stamping Alembic to head...")
subprocess.run(["alembic", "stamp", "head"])

print("Done! Database is ready.")