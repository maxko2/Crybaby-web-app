from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')  # Update connection string as per your MongoDB setup
db = client['Crybaby']  # Replace 'Crybaby' with the name of your database

# Check if the 'Crybaby' database exists
if 'Crybaby' not in client.list_database_names():
    # Create the 'Crybaby' database
    db = client['Crybaby']
    print("Database 'Crybaby' created successfully.")
else:
    db = client['Crybaby']
    print("Database 'Crybaby' already exists.")

# Check if 'users' collection exists in the database
if 'users' not in db.list_collection_names():
    # Create 'users' collection
    users_collection = db['users']
    print("Collection 'users' created successfully.")
else:
    users_collection = db['users']
    print("Collection 'users' already exists.")

# # Delete all documents in the 'users' collection
# result = users_collection.delete_many({})  # Empty filter to match all documents