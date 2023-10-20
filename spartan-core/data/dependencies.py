import logging
import os

from pymongo import MongoClient
from .config import ENV_VERSION, VALUE_UNKNOWN, ENV_MONGODB_URL, VALUE_DEFAULT_DB_NAME

logger = logging.getLogger(__name__)

mongodb_client = MongoClient(os.environ[ENV_MONGODB_URL])
mongodb_client.admin.command('ping')
db = mongodb_client.get_default_database(VALUE_DEFAULT_DB_NAME)
logger.info(f"using db {db.name}")


def get_mongodb_session():
    return db
