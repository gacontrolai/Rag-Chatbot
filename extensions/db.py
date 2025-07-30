from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Sync MongoDB client
mongo_client = None
db = None

# Async MongoDB client (for future use)
async_mongo_client = None
async_db = None

def init_db(app):
    """Initialize MongoDB connection"""
    global mongo_client, db, async_mongo_client, async_db
    
    mongodb_uri = app.config['MONGODB_URI']
    db_name = app.config['MONGODB_DB_NAME']
    print(mongodb_uri)
    # Sync client
    mongo_client = MongoClient(mongodb_uri)
    db = mongo_client[db_name]
    print("connected")
    # Async client (for future async operations)
    # async_mongo_client = AsyncIOMotorClient(mongodb_uri)
    # async_db = async_mongo_client[db_name]
    
    # Test connection
    try:
        mongo_client.admin.command('ping')
        app.logger.info("MongoDB connection successful")
    except Exception as e:
        app.logger.error(f"MongoDB connection failed: {e}")
        raise

def get_db():
    """Get the database instance"""
    return db

def get_async_db():
    """Get the async database instance"""
    return async_db

def close_db():
    """Close database connections"""
    global mongo_client, async_mongo_client
    if mongo_client:
        mongo_client.close()
    if async_mongo_client:
        async_mongo_client.close() 