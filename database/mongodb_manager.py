"""
MongoDB Database Connection and CRUD Operations Module
Handles all MongoDB operations for the AI Prescription Reader System
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MongoDBManager:
    """Manages MongoDB connections and database operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.uri = os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017"
        )
        self.db_name = os.getenv(
            "MONGODB_DB_NAME",
            "ai_prescription_reader"
        )
        self.timeout = int(os.getenv("MONGODB_TIMEOUT", "5000"))
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Establish MongoDB connection
        Returns: bool - True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.timeout,
                connectTimeoutMS=self.timeout
            )
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"MongoDB Connection Error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
        except Exception:
            return False
        return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    def store_prescription_analysis(
        self,
        user_id: str,
        file_name: str,
        medicines: List[Dict],
        dosage: List[Dict],
        benefits: List[Dict],
        interactions: List[Dict],
        recommendations: List[Dict],
        ocr_text: str,
        metadata: Dict = None
    ) -> Optional[str]:
        """
        Store complete prescription analysis in MongoDB
        
        Args:
            user_id: User identifier
            file_name: Original prescription file name
            medicines: List of detected medicines
            dosage: List of dosage information
            benefits: List of medicine benefits
            interactions: List of drug interactions
            recommendations: List of recommendations
            ocr_text: Extracted OCR text from prescription
            metadata: Additional metadata
        
        Returns: Document ID if successful, None if failed
        """
        try:
            prescription_data = {
                "user_id": user_id,
                "file_name": file_name,
                "medicines": medicines,
                "dosage": dosage,
                "benefits": benefits,
                "interactions": interactions,
                "recommendations": recommendations,
                "ocr_text": ocr_text,
                "metadata": metadata or {},
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            collection = self.db["prescriptions"]
            result = collection.insert_one(prescription_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing prescription analysis: {e}")
            return None
    
    def get_prescription_by_id(
        self,
        prescription_id: str
    ) -> Optional[Dict]:
        """
        Retrieve prescription analysis by ID
        
        Args:
            prescription_id: MongoDB prescription document ID
        
        Returns: Prescription document or None if not found
        """
        try:
            from bson import ObjectId
            collection = self.db["prescriptions"]
            prescription = collection.find_one({"_id": ObjectId(prescription_id)})
            if prescription:
                prescription["_id"] = str(prescription["_id"])
            return prescription
        except Exception as e:
            print(f"Error retrieving prescription: {e}")
            return None
    
    def get_user_prescriptions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve all prescriptions for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of prescriptions to retrieve
        
        Returns: List of prescription documents
        """
        try:
            collection = self.db["prescriptions"]
            prescriptions = list(
                collection.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(limit)
            )
            # Convert ObjectId to string
            for p in prescriptions:
                p["_id"] = str(p["_id"])
            return prescriptions
        except Exception as e:
            print(f"Error retrieving user prescriptions: {e}")
            return []
    
    def update_prescription(
        self,
        prescription_id: str,
        update_data: Dict
    ) -> bool:
        """
        Update prescription analysis
        
        Args:
            prescription_id: MongoDB prescription document ID
            update_data: Dictionary of fields to update
        
        Returns: True if successful, False otherwise
        """
        try:
            from bson import ObjectId
            collection = self.db["prescriptions"]
            update_data["updated_at"] = datetime.now()
            
            result = collection.update_one(
                {"_id": ObjectId(prescription_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating prescription: {e}")
            return False
    
    def delete_prescription(self, prescription_id: str) -> bool:
        """
        Delete prescription analysis
        
        Args:
            prescription_id: MongoDB prescription document ID
        
        Returns: True if successful, False otherwise
        """
        try:
            from bson import ObjectId
            collection = self.db["prescriptions"]
            result = collection.delete_one({"_id": ObjectId(prescription_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting prescription: {e}")
            return False
    
    def store_medicine(
        self,
        medicine_data: Dict
    ) -> Optional[str]:
        """
        Store medicine information in MongoDB
        
        Args:
            medicine_data: Dictionary containing medicine information
        
        Returns: Document ID if successful, None if failed
        """
        try:
            collection = self.db["medicines"]
            medicine_data["created_at"] = datetime.now()
            result = collection.insert_one(medicine_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing medicine: {e}")
            return None
    
    def get_medicine(self, name: str) -> Optional[Dict]:
        """
        Retrieve medicine by name
        
        Args:
            name: Medicine name
        
        Returns: Medicine document or None if not found
        """
        try:
            collection = self.db["medicines"]
            medicine = collection.find_one(
                {"name": {"$regex": name, "$options": "i"}}
            )
            if medicine:
                medicine["_id"] = str(medicine["_id"])
            return medicine
        except Exception as e:
            print(f"Error retrieving medicine: {e}")
            return None
    
    def batch_store_medicines(
        self,
        medicines_list: List[Dict]
    ) -> int:
        """
        Store multiple medicines in batch
        
        Args:
            medicines_list: List of medicine dictionaries
        
        Returns: Number of medicines inserted
        """
        try:
            collection = self.db["medicines"]
            for med in medicines_list:
                med["created_at"] = datetime.now()
            
            result = collection.insert_many(
                medicines_list,
                ordered=False
            )
            return len(result.inserted_ids)
        except Exception as e:
            print(f"Error batch storing medicines: {e}")
            return 0
    
    def store_user_report(
        self,
        user_id: str,
        prescription_id: str,
        report_data: Dict
    ) -> Optional[str]:
        """
        Store user report in MongoDB
        
        Args:
            user_id: User identifier
            prescription_id: Associated prescription ID
            report_data: Report content and metadata
        
        Returns: Report document ID if successful, None if failed
        """
        try:
            collection = self.db["reports"]
            report = {
                "user_id": user_id,
                "prescription_id": prescription_id,
                "report_data": report_data,
                "created_at": datetime.now()
            }
            result = collection.insert_one(report)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing report: {e}")
            return None
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics for a collection
        
        Args:
            collection_name: Name of the collection
        
        Returns: Collection statistics
        """
        try:
            collection = self.db[collection_name]
            return {
                "total_documents": collection.count_documents({}),
                "indexes": list(collection.list_indexes())
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Prescriptions indexes
            prescriptions = self.db["prescriptions"]
            prescriptions.create_index("user_id")
            prescriptions.create_index("created_at")
            prescriptions.create_index([("user_id", 1), ("created_at", -1)])
            
            # Medicines indexes
            medicines = self.db["medicines"]
            medicines.create_index("name")
            medicines.create_index("category")
            
            # Reports indexes
            reports = self.db["reports"]
            reports.create_index("user_id")
            reports.create_index("prescription_id")
            
            print("Indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {e}")


# Singleton instance for use throughout the application
@st.cache_resource
def get_mongo_manager() -> MongoDBManager:
    """Get singleton MongoDB manager instance"""
    manager = MongoDBManager()
    if not manager.is_connected():
        raise Exception("Failed to connect to MongoDB")
    manager.create_indexes()
    return manager
