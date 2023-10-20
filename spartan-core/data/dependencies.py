import logging
import os

from minio import Minio
from pymongo import MongoClient
from .config import ENV_VERSION, VALUE_UNKNOWN, ENV_MONGODB_URL, VALUE_DEFAULT_DB_NAME, ENV_S3_ENDPOINT, \
    ENV_S3_ACCESS_KEY, ENV_S3_SECRET_KEY, ENV_S3_SECURE

logger = logging.getLogger(__name__)

mongodb_client = MongoClient(os.environ[ENV_MONGODB_URL])
mongodb_client.admin.command('ping')
mongo_db_session = mongodb_client.get_default_database(VALUE_DEFAULT_DB_NAME)
logger.info(f"using db {mongo_db_session.name}")

s3_session = Minio(
    endpoint=os.environ[ENV_S3_ENDPOINT],
    access_key=os.environ[ENV_S3_ACCESS_KEY],
    secret_key=os.environ[ENV_S3_SECRET_KEY],
    secure='true' == os.environ[ENV_S3_SECURE].lower()
)

found = s3_session.bucket_exists(VALUE_DEFAULT_DB_NAME)
if not found:
    s3_session.make_bucket(VALUE_DEFAULT_DB_NAME)
logger.info(f"using s3 bucket {VALUE_DEFAULT_DB_NAME}")


def get_mongodb_session():
    return mongo_db_session


def get_s3_session():
    return s3_session


def gte_s3_bucket():
    return VALUE_DEFAULT_DB_NAME
