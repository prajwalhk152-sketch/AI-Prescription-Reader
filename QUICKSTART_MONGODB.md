# MongoDB Integration Quick Start

## What's Been Integrated

MongoDB has been fully integrated into Module 12 for:
- ✓ Prescription analysis storage
- ✓ Medicine reference data storage
- ✓ Report metadata tracking
- ✓ User prescription history

## Quick Start (5 minutes)

### Step 1: Install MongoDB

**Windows:**
```powershell
# Using Chocolatey
choco install mongodb

# Then start MongoDB (usually starts automatically)
```

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongod
```

### Step 2: Install Python Packages

```bash
pip install -r requirements.txt
```

This will install `pymongo` and `python-dotenv`.

### Step 3: Verify Installation

```bash
python database/init_db.py
```

You should see:
```
MongoDB Connection verified
✓ Indexes created successfully
```

### Step 4: (Optional) Run Tests

```bash
python database/test_mongodb.py
```

### Step 5: Run Streamlit App

```bash
streamlit run app.py
```

Go to **Module 12** to use MongoDB features!

## Files Created/Modified

### New Files
- `database/mongodb_manager.py` - MongoDB connection and CRUD operations
- `database/init_db.py` - Database initialization utility
- `database/test_mongodb.py` - Comprehensive testing suite
- `database/__init__.py` - Package initialization
- `.env` - Configuration file (local MongoDB settings)
- `.env.example` - Example configuration
- `.gitignore` - Updated to ignore .env
- `MONGODB_SETUP.md` - Comprehensive setup guide

### Modified Files
- `requirements.txt` - Added `pymongo==4.6.1` and `python-dotenv==1.0.0`
- `modules/module_12_database_storage.py` - Complete rewrite with MongoDB integration

## Module 12 Features

### 1. Store Analysis Tab
- Automatically collects data from Modules 6-10
- Stores everything in MongoDB
- Get prescription ID for tracking

### 2. View Prescriptions Tab
- Search prescriptions by User ID
- View all prescription details
- Delete prescriptions

### 3. Generate Report Tab
- Generate PDF from MongoDB data
- Download PDF locally
- Store report metadata

### 4. Database Statistics Tab
- View collection statistics
- Monitor database health
- Check connection status

## MongoDB Collections

### Prescriptions
- Stores complete prescription analyses
- Indexed by user_id and created_at
- Contains all analysis data

### Medicines
- Reference database of medicines
- Indexed by name and category
- Supports searches

### Reports
- Tracks generated reports
- Linked to prescriptions
- Metadata storage

## API Usage Examples

```python
from database.mongodb_manager import get_mongo_manager

# Get manager
db_manager = get_mongo_manager()

# Store prescription
prescription_id = db_manager.store_prescription_analysis(
    user_id="user_001",
    file_name="prescription.jpg",
    medicines=[...],
    dosage=[...],
    # ... other data
)

# Retrieve prescriptions
prescriptions = db_manager.get_user_prescriptions("user_001")

# Get collection stats
stats = db_manager.get_collection_stats("prescriptions")
```

## Troubleshooting

**MongoDB not running?**
```bash
# Check status
mongosh

# If not connected, start MongoDB:
mongod  # Windows
brew services start mongodb-community  # macOS
sudo systemctl start mongod  # Linux
```

**Import errors?**
```bash
pip install pymongo python-dotenv
```

**Connection denied?**
- Make sure MongoDB is running on localhost:27017
- Check .env file for correct MONGODB_URI
- Verify no firewall blocks the connection

## Next Steps

1. ✓ Install MongoDB
2. ✓ Install packages: `pip install -r requirements.txt`
3. ✓ Verify setup: `python database/init_db.py`
4. ✓ Run app: `streamlit run app.py`
5. ✓ Use Module 12 for database operations

## Full Documentation

For detailed information, see `MONGODB_SETUP.md`

---

**Questions or Issues?**
- Check MongoDB logs
- Review error messages in Streamlit
- See troubleshooting section in MONGODB_SETUP.md
