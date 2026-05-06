#!/usr/bin/env python3
"""
Database migration script to remove name column from users table.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env file")
    exit(1)

print(f"Connecting to database: {DATABASE_URL}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Connect and run migrations
    with engine.connect() as connection:
        print("Running migration: Remove name column from users table...")
        
        # Drop name column if it exists
        connection.execute(text("""
            ALTER TABLE users
            DROP COLUMN IF EXISTS name;
        """))
        
        # Commit changes
        connection.commit()
        
    print("✅ Migration completed successfully!")
    print("\nName column has been removed from users table.")
    
except Exception as e:
    print(f"❌ Migration failed: {str(e)}")
    exit(1)
