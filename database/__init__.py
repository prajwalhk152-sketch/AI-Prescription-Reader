"""
Database package for AI Prescription Reader
Provides MongoDB connectivity and database operations
"""

from database.mongodb_manager import MongoDBManager, get_mongo_manager

__all__ = ['MongoDBManager', 'get_mongo_manager']
