#!/usr/bin/env python3
"""
Database migration: Add CANCELLED status to JobStatus enum.

Run this script to update the database enum to include the new CANCELLED status.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal, engine
from backend.core.logging import setup_logging
from backend.core.config import get_settings
from sqlalchemy import text

def migrate():
    """Add CANCELLED status to JobStatus enum."""
    settings = get_settings()
    setup_logging(settings.log_level, settings.environment)
    
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("Adding CANCELLED status to JobStatus enum")
        print("=" * 80)
        
        # PostgreSQL: Add new enum value
        # Note: PostgreSQL allows adding enum values
        db.execute(text("""
            DO $$ BEGIN
                ALTER TYPE jobstatus ADD VALUE IF NOT EXISTS 'cancelled';
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        db.commit()
        
        print("✅ Successfully added CANCELLED status to JobStatus enum")
        print("=" * 80)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        print("\nIf the enum value already exists, this is safe to ignore.")
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    migrate()




