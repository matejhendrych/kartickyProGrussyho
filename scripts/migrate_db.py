#!/usr/bin/env python3
"""
Database migration script
Migrates data from SQLite/MySQL to PostgreSQL
"""
import argparse
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def migrate_database(source_url: str, target_url: str, verbose: bool = False):
    """
    Migrate database from source to target
    
    Args:
        source_url: Source database URL
        target_url: Target database URL
        verbose: Print detailed information
    """
    print(f"Migrating from {source_url} to {target_url}")
    
    # Create engines
    source_engine = create_engine(source_url, poolclass=NullPool)
    target_engine = create_engine(target_url, poolclass=NullPool)
    
    # Reflect source database structure
    source_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)
    
    # Create tables in target database
    print("Creating tables in target database...")
    source_metadata.create_all(target_engine)
    
    # Create sessions
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    source_session = SourceSession()
    target_session = TargetSession()
    
    try:
        # Get all table names
        tables = source_metadata.sorted_tables
        
        for table in tables:
            print(f"Migrating table: {table.name}")
            
            # Read all data from source
            source_data = source_session.execute(table.select()).fetchall()
            
            if verbose:
                print(f"  Found {len(source_data)} rows")
            
            # Insert into target
            if source_data:
                # Convert to dictionaries
                rows = []
                for row in source_data:
                    row_dict = dict(row._mapping)
                    rows.append(row_dict)
                
                # Bulk insert
                target_session.execute(table.insert(), rows)
                target_session.commit()
                
                if verbose:
                    print(f"  Inserted {len(rows)} rows")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        target_session.rollback()
        raise
    finally:
        source_session.close()
        target_session.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Migrate database from one backend to another'
    )
    parser.add_argument(
        '--from',
        dest='source',
        required=True,
        help='Source database URL (e.g., sqlite:///dev.db)'
    )
    parser.add_argument(
        '--to',
        dest='target',
        required=True,
        help='Target database URL (e.g., postgresql://user:pass@localhost/dbname)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        migrate_database(args.source, args.target, args.verbose)
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
