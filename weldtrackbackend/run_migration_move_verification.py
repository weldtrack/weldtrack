#!/usr/bin/env python3
"""
Database migration script to move email verification to separate table.
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
        print("Running migration: Move email verification to separate table...")
        
        # Step 1: Create email_verifications table
        print("  → Creating email_verifications table...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE NOT NULL,
                verification_code VARCHAR(6),
                code_expires_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            );
        """))
        
        # Step 2: Migrate data from users table to email_verifications table
        print("  → Migrating data from users table...")
        connection.execute(text("""
            INSERT INTO email_verifications (user_id, is_verified, verification_code, code_expires_at)
            SELECT id, COALESCE(email_verified, FALSE), verification_code, code_expires_at
            FROM users
            ON CONFLICT (user_id) DO NOTHING;
        """))
        
        # Step 3: Drop columns from users table
        print("  → Removing columns from users table...")
        connection.execute(text("""
            ALTER TABLE users
            DROP COLUMN IF EXISTS email_verified,
            DROP COLUMN IF EXISTS verification_code,
            DROP COLUMN IF EXISTS code_expires_at;
        """))
        
        # Commit changes
        connection.commit()
        
    print("✅ Migration completed successfully!")
    print("\nChanges made:")
    print("  • Created email_verifications table")
    print("  • Migrated data from users table")
    print("  • Removed email_verified, verification_code, code_expires_at from users table")
    
except Exception as e:
    print(f"❌ Migration failed: {str(e)}")
    exit(1)
