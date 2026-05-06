#!/usr/bin/env python3
"""
Database migration script to add email verification support.
Run this script to apply the migration to your database.
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
        print("Running migration: Add email verification...")
        
        # Step 1: Add columns to users table
        print("  → Adding columns to users table...")
        connection.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE NOT NULL,
            ADD COLUMN IF NOT EXISTS verification_code VARCHAR(6),
            ADD COLUMN IF NOT EXISTS code_expires_at TIMESTAMP WITH TIME ZONE;
        """))
        
        # Step 2: Create email_verification_codes table
        print("  → Creating email_verification_codes table...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS email_verification_codes (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(6) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """))
        
        # Step 3: Create index
        print("  → Creating index...")
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_email_verification_codes_email 
            ON email_verification_codes(email);
        """))
        
        # Commit changes
        connection.commit()
        
    print("✅ Migration completed successfully!")
    print("\nYou can now start the server with: python -m app.main")
    
except Exception as e:
    print(f"❌ Migration failed: {str(e)}")
    exit(1)
