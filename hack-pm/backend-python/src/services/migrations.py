"""
Database migration utilities
"""
import sqlite3
import logging
from typing import List, Tuple
from .database import engine, DATABASE_URL

logger = logging.getLogger(__name__)

class Migration:
    def __init__(self, version: int, description: str, sql: str):
        self.version = version
        self.description = description
        self.sql = sql

# Define migrations
MIGRATIONS: List[Migration] = [
    Migration(
        version=1,
        description="Add time-boxed development fields to issues table",
        sql="""
        ALTER TABLE issues ADD COLUMN estimated_hours INTEGER;
        ALTER TABLE issues ADD COLUMN deadline DATETIME;
        ALTER TABLE issues ADD COLUMN time_box_start DATETIME;
        ALTER TABLE issues ADD COLUMN time_box_end DATETIME;
        ALTER TABLE issues ADD COLUMN priority_escalated BOOLEAN DEFAULT FALSE;
        ALTER TABLE issues ADD COLUMN hackathon_phase TEXT;
        """
    ),
    Migration(
        version=2,
        description="Create hackathon_timeboxes table if not exists",
        sql="""
        CREATE TABLE IF NOT EXISTS hackathon_timeboxes (
            id INTEGER PRIMARY KEY,
            repo_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phase TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repo_id) REFERENCES repos (id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_timebox_repo_active ON hackathon_timeboxes (repo_id, is_active);
        CREATE INDEX IF NOT EXISTS idx_timebox_phase ON hackathon_timeboxes (repo_id, phase);
        """
    )
]

def get_current_version() -> int:
    """Get current database schema version"""
    try:
        if "sqlite" in DATABASE_URL:
            db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create migrations table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    description TEXT,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Get current version
            cursor.execute("SELECT MAX(version) FROM schema_migrations")
            result = cursor.fetchone()
            version = result[0] if result[0] is not None else 0
            
            conn.close()
            return version
    except Exception as e:
        logger.error(f"Error getting current version: {e}")
        return 0

def apply_migration(migration: Migration) -> bool:
    """Apply a single migration"""
    try:
        if "sqlite" in DATABASE_URL:
            db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Execute migration SQL (handle multiple statements)
            statements = [stmt.strip() for stmt in migration.sql.split(';') if stmt.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        logger.info(f"Column/table already exists, skipping: {e}")
                        continue
                    else:
                        raise
            
            # Record migration
            cursor.execute(
                "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                (migration.version, migration.description)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Applied migration {migration.version}: {migration.description}")
            return True
            
    except Exception as e:
        logger.error(f"Error applying migration {migration.version}: {e}")
        return False

def run_migrations() -> bool:
    """Run all pending migrations"""
    try:
        current_version = get_current_version()
        logger.info(f"Current database version: {current_version}")
        
        pending_migrations = [m for m in MIGRATIONS if m.version > current_version]
        
        if not pending_migrations:
            logger.info("No pending migrations")
            return True
        
        logger.info(f"Found {len(pending_migrations)} pending migrations")
        
        for migration in pending_migrations:
            if not apply_migration(migration):
                logger.error(f"Failed to apply migration {migration.version}")
                return False
        
        logger.info("All migrations applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    try:
        if "sqlite" in DATABASE_URL:
            db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            conn.close()
            return column_name in columns
    except Exception as e:
        logger.error(f"Error checking column existence: {e}")
        return False