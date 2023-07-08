import os

MYSQL_USERNAME = os.getenv('MYSQL_USER', 'db_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'db_pass')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOST', 'mariadb')
MYSQL_DBNAME = os.getenv('MYSQL_DATABASE', 'citrouille-db')
MYSQL_TABLE_TOKENS = 'tokens'
MYSQL_TABLE_OBJECTS = 'objects'

MYSQL_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DBNAME}"

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minio_access_key')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minio_secret_key')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'citrouille-bucket')
