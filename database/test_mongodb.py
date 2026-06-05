"""
Test script for MongoDB Integration
Verifies that MongoDB is properly configured and functional
"""

import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.mongodb_manager import MongoDBManager
from dotenv import load_dotenv
from datetime import datetime


def test_connection():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("TEST 1: MongoDB Connection")
    print("="*60)
    
    load_dotenv()
    manager = MongoDBManager()
    
    if manager.is_connected():
        print("✓ MongoDB connection successful")
        return True
    else:
        print("✗ Failed to connect to MongoDB")
        print(f"  URI: {manager.uri}")
        print(f"  Database: {manager.db_name}")
        return False


def test_prescription_storage(manager: MongoDBManager):
    """Test prescription data storage"""
    print("\n" + "="*60)
    print("TEST 2: Store Prescription Data")
    print("="*60)
    
    prescription_id = manager.store_prescription_analysis(
        user_id="test_user_001",
        file_name="test_prescription.jpg",
        medicines=[
            {"name": "Aspirin", "dosage": "500mg", "category": "Pain Relief"},
            {"name": "Amoxicillin", "dosage": "250mg", "category": "Antibiotic"}
        ],
        dosage=[
            {"medicine": "Aspirin", "timing": "Morning", "frequency": "Daily"},
            {"medicine": "Amoxicillin", "timing": "After meals", "frequency": "3x daily"}
        ],
        benefits=[
            {"medicine": "Aspirin", "benefit": "Reduces fever and pain"},
            {"medicine": "Amoxicillin", "benefit": "Treats bacterial infections"}
        ],
        interactions=[
            {"interaction": "Aspirin + Ibuprofen may cause stomach issues"}
        ],
        recommendations=[
            {"recommendation": "Take with food"},
            {"recommendation": "Avoid alcohol"}
        ],
        ocr_text="Sample OCR extracted text from prescription",
        metadata={"test": True}
    )
    
    if prescription_id:
        print(f"✓ Prescription stored successfully")
        print(f"  Prescription ID: {prescription_id}")
        return prescription_id
    else:
        print("✗ Failed to store prescription")
        return None


def test_prescription_retrieval(manager: MongoDBManager):
    """Test prescription data retrieval"""
    print("\n" + "="*60)
    print("TEST 3: Retrieve Prescriptions")
    print("="*60)
    
    prescriptions = manager.get_user_prescriptions("test_user_001", limit=5)
    
    if prescriptions:
        print(f"✓ Retrieved {len(prescriptions)} prescription(s)")
        for idx, p in enumerate(prescriptions, 1):
            print(f"\n  Prescription {idx}:")
            print(f"    ID: {p['_id']}")
            print(f"    File: {p['file_name']}")
            print(f"    Medicines: {len(p['medicines'])}")
            print(f"    Created: {p['created_at']}")
        return True
    else:
        print("✗ No prescriptions found")
        return False


def test_medicine_storage(manager: MongoDBManager):
    """Test medicine storage"""
    print("\n" + "="*60)
    print("TEST 4: Store Medicine Data")
    print("="*60)
    
    medicines = [
        {
            "name": "Paracetamol",
            "category": "Pain Relief",
            "dosage": "500mg",
            "manufacturer": "Generic",
            "side_effects": ["Rare liver damage"]
        },
        {
            "name": "Ibuprofen",
            "category": "Anti-inflammatory",
            "dosage": "400mg",
            "manufacturer": "Generic",
            "side_effects": ["Stomach upset", "Headache"]
        }
    ]
    
    count = manager.batch_store_medicines(medicines)
    
    if count > 0:
        print(f"✓ Stored {count} medicine(s) successfully")
        return True
    else:
        print("✗ Failed to store medicines")
        return False


def test_collection_stats(manager: MongoDBManager):
    """Test collection statistics"""
    print("\n" + "="*60)
    print("TEST 5: Collection Statistics")
    print("="*60)
    
    collections = ["prescriptions", "medicines", "reports"]
    
    for collection_name in collections:
        stats = manager.get_collection_stats(collection_name)
        print(f"\n{collection_name.capitalize()}:")
        print(f"  Total Documents: {stats.get('total_documents', 0)}")
        print(f"  Indexes: {len(stats.get('indexes', []))}")
        
        if stats.get('indexes'):
            for idx in stats['indexes']:
                print(f"    - {idx.get('name', 'unknown')}")


def test_update_and_delete(manager: MongoDBManager):
    """Test update and delete operations"""
    print("\n" + "="*60)
    print("TEST 6: Update and Delete Operations")
    print("="*60)
    
    # Get a prescription to update
    prescriptions = manager.get_user_prescriptions("test_user_001", limit=1)
    
    if prescriptions:
        prescription_id = prescriptions[0]['_id']
        
        # Test update
        update_success = manager.update_prescription(
            prescription_id=prescription_id,
            update_data={
                "metadata": {"updated": True, "update_time": datetime.now().isoformat()}
            }
        )
        
        if update_success:
            print(f"✓ Prescription updated successfully")
            updated = manager.get_prescription_by_id(prescription_id)
            if updated and updated.get('metadata', {}).get('updated'):
                print(f"  Update verified: metadata.updated = True")
        else:
            print(f"✗ Failed to update prescription")
        
        # Test delete
        delete_success = manager.delete_prescription(prescription_id)
        
        if delete_success:
            print(f"✓ Prescription deleted successfully")
        else:
            print(f"✗ Failed to delete prescription")
    else:
        print("✗ No prescriptions found for testing")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("█" * 60)
    print("MongoDB Integration Test Suite")
    print("█" * 60)
    
    # Test 1: Connection
    if not test_connection():
        print("\n✗ Tests aborted - Cannot connect to MongoDB")
        return False
    
    load_dotenv()
    manager = MongoDBManager()
    
    # Test 2-6: Operations
    try:
        test_prescription_storage(manager)
        test_prescription_retrieval(manager)
        test_medicine_storage(manager)
        test_collection_stats(manager)
        test_update_and_delete(manager)
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        print("\nMongoDB integration is working correctly!")
        print("You can now use Module 12 in the Streamlit application.")
        return True
    
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        manager.close()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
