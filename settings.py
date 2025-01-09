import os

DOWNLOADS_FOLDER = "/tmp"

MIMETYPES_WHITELIST = ["xls", "xlsx"]

PREMIUM_GRAPHQL_URL = os.environ.get("PREMIUM_GRAPHQL_URL")

REST_API_URL = os.environ.get("REST_API_URL")


PREMIUM_AWS_ACCESS_KEY_ID = os.environ.get("PREMIUM_AWS_ACCESS_KEY_ID")

PREMIUM_AWS_SECRET_ACCESS_KEY = os.environ.get("PREMIUM_AWS_SECRET_ACCESS_KEY")

PREMIUM_AWS_REGION = os.environ.get("PREMIUM_AWS_REGION")

PREMIUM_AWS_BUCKET_NAME = os.environ.get("PREMIUM_AWS_BUCKET_NAME")

PREMIUM_AWS_S3_URL = os.environ.get("PREMIUM_AWS_S3_URL")

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS").split(",")