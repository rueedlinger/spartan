import logging

from minio import Minio
from pymongo import MongoClient
from .config.app_settings import Settings, VALUE_DEFAULT_DB_NAME

logger = logging.getLogger("spartan." + __name__)

settings = Settings()

logger.info(f"init mongodb session...")
mongodb_client = MongoClient(settings.spartan_mongodb_url)
mongodb_client.admin.command('ping')
logger.info(f"checking mongodb db...")
mongo_db_session = mongodb_client.get_default_database(VALUE_DEFAULT_DB_NAME)

logger.info(f"init s3 session...")
s3_session = Minio(
    endpoint=settings.spartan_s3_endpoint,
    access_key=settings.spartan_s3_access_key,
    secret_key=settings.spartan_s3_secret_key,
    secure=settings.spartan_s3_secure
)

logger.info(f"checking s3 bucket...")
found = s3_session.bucket_exists(VALUE_DEFAULT_DB_NAME)
if not found:
    s3_session.make_bucket(VALUE_DEFAULT_DB_NAME)


def get_mongodb_session():
    return mongo_db_session


def get_s3_session():
    return s3_session


def gte_s3_bucket():
    return VALUE_DEFAULT_DB_NAME
