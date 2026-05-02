"""
Database Initialization Script
Creates all tables in PostgreSQL
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import engine, Base, is_db_available
from app.db.models import (
    User,
    IntelligenceReport,
    Headline,
    MarketData,
    CacheEntry
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database tables"""
    
    if not is_db_available():
        logger.error("❌ PostgreSQL not available")
        logger.error("   Make sure PostgreSQL is running:")
        logger.error("   docker-compose up -d postgres")
        return False
    
    try:
        logger.info("🔄 Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully")
        logger.info("\nTables created:")
        logger.info("  • users")
        logger.info("  • intelligence_reports")
        logger.info("  • headlines")
        logger.info("  • market_data")
        logger.info("  • cache_entries")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    
    if not is_db_available():
        logger.error("❌ PostgreSQL not available")
        return False
    
    try:
        logger.warning("⚠️  Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (DESTRUCTIVE!)"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        confirm = input("⚠️  This will DELETE ALL DATA. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            drop_all_tables()
            init_database()
        else:
            logger.info("❌ Cancelled")
    else:
        init_database()
