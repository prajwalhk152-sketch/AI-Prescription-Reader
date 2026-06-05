# MongoDB Integration Setup Guide

## Overview

MongoDB has been integrated into Module 12 (Database Storage) to provide robust, scalable document storage for prescription analyses, medicine information, and generated reports.

## Installation & Setup

### 1. Install MongoDB

#### Windows:
```powershell
# Using Chocolatey (recommended)
choco install mongodb

# Or download from: https://www.mongodb.com/try/download/community
```

#### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install -y mongodb
```

### 2. Start MongoDB Service

#### Windows:
```powershell
# MongoDB should start automatically after installation
# To manually start:
mongod --dbpath "C:\data\db"

# Or if installed as a service:
net start MongoDB
```

#### macOS:
```bash
# Using Homebrew services
brew services start mongodb-community
```

#### Linux:
```bash
# Start MongoDB service
sudo systemctl start mongod

# Check status
sudo systemctl status mongod
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB Connection Settings
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=ai_prescription_reader
MONGODB_TIMEOUT=5000

# Optional: For MongoDB Atlas (Cloud)
# MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority
```

### 4. Install Required Python Packages

```bash
pip install pymongo==4.6.1 python-dotenv==1.0.0
```

Or update from requirements.txt:

```bash
pip install -r requirements.txt
```

## MongoDB Manager Functions

### Core Functions

**Connection Management:**
- `MongoDBManager()` - Initialize connection
- `.is_connected()` - Check connection status
- `.close()` - Close connection

**Prescription Storage:**
- `.store_prescription_analysis()` - Store complete prescription data
- `.get_prescription_by_id()` - Retrieve prescription by ID
- `.get_user_prescriptions()` - Get all prescriptions for a user
- `.update_prescription()` - Update prescription data
- `.delete_prescription()` - Delete prescription

**Medicine Management:**
- `.store_medicine()` - Store single medicine
- `.get_medicine()` - Retrieve medicine by name
- `.batch_store_medicines()` - Store multiple medicines

**Reports:**
- `.store_user_report()` - Store PDF report metadata

**Administration:**
- `.get_collection_stats()` - Get collection statistics
- `.create_indexes()` - Create database indexes

## Database Collections

### 1. Prescriptions Collection
Stores complete prescription analysis:
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "file_name": "string",
  "medicines": [Array],
  "dosage": [Array],
  "benefits": [Array],
  "interactions": [Array],
  "recommendations": [Array],
  "ocr_text": "string",
  "metadata": {Object},
  "created_at": "DateTime",
  "updated_at": "DateTime"
}
```

### 2. Medicines Collection
Stores medicine reference data:
```json
{
  "_id": "ObjectId",
  "name": "string",
  "category": "string",
  "created_at": "DateTime"
}
```

### 3. Reports Collection
Stores PDF report metadata:
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "prescription_id": "ObjectId",
  "report_data": {Object},
  "created_at": "DateTime"
}
```

## Usage Examples

### Store Prescription Analysis

```python
from database.mongodb_manager import get_mongo_manager

db_manager = get_mongo_manager()

prescription_id = db_manager.store_prescription_analysis(
    user_id="user_001",
    file_name="prescription.jpg",
    medicines=[{"name": "Aspirin", "dosage": "500mg"}],
    dosage=[{"timing": "Morning", "frequency": "Daily"}],
    benefits=[{"benefit": "Pain relief"}],
    interactions=[{"warning": "May interact with X"}],
    recommendations=[{"recommendation": "Take with water"}],
    ocr_text="Extracted text from prescription",
    metadata={"analyzed_date": "2026-06-02"}
)
```

### Retrieve User Prescriptions

```python
prescriptions = db_manager.get_user_prescriptions(
    user_id="user_001",
    limit=10
)

for prescription in prescriptions:
    print(f"ID: {prescription['_id']}")
    print(f"File: {prescription['file_name']}")
    print(f"Medicines: {len(prescription['medicines'])}")
```

### Update Prescription

```python
updated = db_manager.update_prescription(
    prescription_id="507f1f77bcf86cd799439011",
    update_data={
        "medicines": updated_medicines_list,
        "notes": "Updated with additional information"
    }
)
```

### Get Database Statistics

```python
stats = db_manager.get_collection_stats("prescriptions")
print(f"Total prescriptions: {stats['total_documents']}")
print(f"Indexes: {stats['indexes']}")
```

## Streamlit Module 12 Features

### Tab 1: Store Analysis
- Upload prescription data from Module 6-10 outputs
- Store complete analysis in MongoDB
- Get prescription ID for future reference

### Tab 2: View Prescriptions
- Retrieve all prescriptions for a user
- View detailed analysis (medicines, dosage, benefits, interactions)
- Delete prescriptions as needed

### Tab 3: Generate Report
- Generate PDF reports from stored MongoDB data
- Download PDF locally
- Store report metadata in MongoDB

### Tab 4: Database Statistics
- View collection statistics
- Monitor database health
- Check connection status

## Troubleshooting

### Connection Issues

**Error: "Failed to connect to MongoDB"**

1. Verify MongoDB is running:
   ```bash
   mongosh  # or mongo in older versions
   ```

2. Check connection string in `.env`

3. Ensure localhost:27017 is accessible

### Permission Errors

**Error: "User not authorized"**

1. Check MongoDB user credentials if using authentication
2. Verify user has read/write permissions on the database
3. For local development, disable authentication (not recommended for production)

### Collection Issues

**Missing data after restart:**

1. MongoDB may have cleared on restart
2. Re-run data import from Module 6-10
3. Check MongoDB data persistence settings

## MongoDB Indexing

Indexes are automatically created for better performance:

- `prescriptions.user_id` - Fast user lookups
- `prescriptions.created_at` - Date-based queries
- `prescriptions.user_id + created_at` - Combined queries
- `medicines.name` - Medicine lookups
- `medicines.category` - Category filtering
- `reports.user_id` - Report retrieval
- `reports.prescription_id` - Prescription linking

## Production Deployment

For production use, consider:

1. **MongoDB Atlas** (Cloud)
   - Fully managed MongoDB service
   - Automatic backups
   - SSL/TLS encryption
   - Global clusters

2. **Authentication**
   - Enable user authentication
   - Use strong passwords
   - Implement role-based access control

3. **Backup Strategy**
   - Regular backup schedules
   - Test restoration procedures
   - Store backups securely

4. **Monitoring**
   - Monitor database performance
   - Set up alerts for issues
   - Track storage usage

## Next Steps

1. ✓ Install MongoDB
2. ✓ Configure `.env` file
3. ✓ Run database initialization: `python database/init_db.py`
4. ✓ Start Streamlit app: `streamlit run app.py`
5. ✓ Go to Module 12 for MongoDB operations

## Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoDB Community Server](https://www.mongodb.com/try/download/community)

## Support

For issues or questions:
1. Check MongoDB logs: `mongod --logpath=./logs/mongod.log`
2. Verify connection with: `python database/init_db.py`
3. Review error messages in Streamlit UI
