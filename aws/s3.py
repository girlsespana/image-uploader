import datetime
import os
import uuid

import boto3

import settings


class S3UploaderError(Exception):
    pass


class S3FileUploader:
    def __init__(self, path: str):
        self.path = path
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.PREMIUM_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.PREMIUM_AWS_SECRET_ACCESS_KEY,
        )

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def formatted_current_date(self):
        current_date = datetime.datetime.now().date()
        return current_date.strftime("%Y/%m/%d")

    @property
    def s3_path(self) -> str:
        # Add UUID to filename to avoid cache issues
        name, ext = os.path.splitext(self.filename)
        unique_filename = f"{name}-{uuid.uuid4().hex[:8]}{ext}"
        return (
            f"uploads/model-images/"
            f"{self.formatted_current_date}/{unique_filename}"
        )

    def upload(self):
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Uploading to S3: bucket={settings.PREMIUM_AWS_BUCKET_NAME}, path={self.s3_path}")

        try:
            with open(self.path, "rb") as f:
                self.client.upload_fileobj(
                    f,
                    settings.PREMIUM_AWS_BUCKET_NAME,
                    self.s3_path,
                    ExtraArgs={'ACL': 'public-read'}
                )
            logger.info(f"S3 upload completed successfully")
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise S3UploaderError(str(e))

        url = f'{settings.PREMIUM_AWS_S3_URL}{self.s3_path}'
        logger.info(f"Returning URL: {url}")
        return url
