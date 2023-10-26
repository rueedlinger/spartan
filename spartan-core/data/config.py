import json
import logging
import os

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

VALUE_UNKNOWN = 'UNKNOWN'

info_file = open(os.path.join(os.getcwd(), 'conf/app.json'))
data = json.load(info_file)
info_file.close()

APP_NAME = data["app-name"]
VERSION = data['app-version']
VALUE_DEFAULT_DB_NAME = data['db-name']

logger.info(f"app-name: {APP_NAME}")
logger.info(f"ap-version: {VERSION}")
logger.info(f"db-name: {VALUE_DEFAULT_DB_NAME}")


class Settings(BaseSettings):
    spartan_mongodb_url: str = "mongodb://root:example@localhost:27017/spartan?authSource=admin"
    spartan_s3_endpoint: str = "localhost:9000"
    spartan_s3_access_key: str = "root"
    spartan_s3_secret_key: str = "secret-key"
    spartan_s3_secure: bool = False
