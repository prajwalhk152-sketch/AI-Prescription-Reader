"""
Database Initialization and Setup Module
Helps configure and initialize MongoDB for the AI Prescription Reader System
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.mongodb_manager import MongoDBManager
from dotenv import load_dotenv


def setup_mongodb():
    """
    Setup MongoDB connection and create initial collections
    """
    load_dotenv()
    
    print("=" * 60)
    print("MongoDB Setup for AI Prescription Reader")
    print("=" * 60)
    
    # Get MongoDB configuration
    mongodb_uri = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017"
    )
    mongodb_db = os.getenv(
        "MONGODB_DB_NAME",
        "ai_prescription_reader"
    )
    
    print(f"\nMongoDB Configuration:")
    print(f"  URI: {mongodb_uri}")
    print(f"  Database: {mongodb_db}")
    
    # Initialize MongoDB Manager
    print("\nConnecting to MongoDB...")
    manager = MongoDBManager()
    
    if manager.is_connected():
        print("✓ Successfully connected to MongoDB")
        
        # Create indexes
        print("\nCreating database indexes...")
        manager.create_indexes()
        print("✓ Indexes created successfully")
        
        # Display collection information
        print("\nDatabase Collections:")
        try:
            for collection_name in manager.db.list_collection_names():
                collection = manager.db[collection_name]
                doc_count = collection.count_documents({})
                print(f"  - {collection_name}: {doc_count} documents")
        except Exception as e:
            print(f"  Error retrieving collections: {e}")
        
        print("\n✓ MongoDB setup completed successfully!")
        return True
    else:
        print("✗ Failed to connect to MongoDB")
        print("\nTroubleshooting steps:")
        print("1. Ensure MongoDB is installed and running")
        print("2. Check .env file for correct MONGODB_URI")
        print("3. For local MongoDB: mongodb://localhost:27017")
        print("4. For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
        return False


def verify_connection():
    """
    Verify MongoDB connection without setup
    """
    load_dotenv()
    
    manager = MongoDBManager()
    
    if manager.is_connected():
        print("✓ MongoDB connection verified")
        return True
    else:
        print("✗ Failed to connect to MongoDB")
        return False


if __name__ == "__main__":
    setup_mongodb()
