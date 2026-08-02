import os
import sys
from pathlib import Path

# 1. Load environment variables from .env immediately
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# 2. Setup project root path for internal application utility imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine
from app.db import Base
import app.models 
import subprocess

# 3. Get the URL
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

# 4. Create tables using SQLAlchemy
print("Building database tables...")
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

# 5. Stamp Alembic using the shell
print("Stamping Alembic to head...")
subprocess.run(["alembic", "stamp", "head"])

print("Done! Database is ready.")