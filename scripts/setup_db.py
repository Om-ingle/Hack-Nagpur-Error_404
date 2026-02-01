#!/usr/bin/env python3
"""
Database Setup and Migration Script
Creates all tables and inserts sample data
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.schema import initialize_database


def main():
    """Initialize database with tables and sample data"""
    try:
        print("=" * 50)
        print("🗄️  AarogyaQueue Database Setup")
        print("=" * 50)
        print()
        
        print("📋 Creating/updating database tables...")
        initialize_database()
        
        print("✓ Database tables ready")
        print()
        print("=" * 50)
        print("✓ Database Setup Complete!")
        print("=" * 50)
        print()
        print("📋 Sample Login Credentials:")
        print("-" * 50)
        print("  SENIOR Doctor: Role=SENIOR, PIN=1234")
        print("  JUNIOR Doctor: Role=JUNIOR, PIN=5678")
        print("  SENIOR Doctor: Role=SENIOR, PIN=9999")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
