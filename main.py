import os
import logging

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.params import Header
from fastapi.middleware.cors import CORSMiddleware

import settings
import requests

from aws.s3 import S3FileUploader, S3UploaderError
from utils.files import sanitize_filename
from utils.watermark import apply_watermark

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class TokenError(Exception):
    pass


def verify_token(token):
    url = settings.PREMIUM_GRAPHQL_URL
    query = """query Me { me { id } }"""

    headers = {
        "Authorization": F"JWT {token}",
        "Content-Type": "application/json",
    }

    logger.info(f"Verifying token, first 20 chars: {token[:20]}...")

    response = requests.post(url, json={"query": query}, headers=headers)
    response = response.json()

    logger.info(f"Token verification response: {response}")

    data = response.get("data")

    me = data.get("me")

    if not me:
        logger.error(f"Token verification failed. Response: {response}")
        raise TokenError("Unable to authenticate with provided token")


@app.post("/uploadImage")
async def upload_image(
        image: UploadFile,
        Authorization: str = Header(...),
):
    logger.info("=" * 50)
    logger.info(f"Received upload request")
    logger.info(f"Image filename: {image.filename}")
    logger.info(f"Content-Type: {image.content_type}")
    logger.info(f"Authorization header (first 30 chars): {Authorization[:30]}...")

    allowed_extensions = ["jpg", "jpeg", "png", "mp4"]
    ext = image.filename.split(".")[-1]

    logger.info(f"File extension: {ext}")
    logger.info(f"Allowed extensions: {allowed_extensions}")

    try:
        logger.info("Attempting to verify token...")
        verify_token(Authorization)
        logger.info("Token verified successfully")
    except TokenError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(status_code=400, detail=f"Token verification error: {str(e)}")

    if ext not in allowed_extensions:
        logger.error(f"File extension {ext} not in allowed extensions")
        raise HTTPException(status_code=400,
                            detail="File type is not supported")

    temp_file_path = str(os.path.join(
        settings.DOWNLOADS_FOLDER,
        sanitize_filename(image.filename)
    ))

    logger.info(f"Temp file path: {temp_file_path}")

    with open(temp_file_path, "wb+") as buffer:
        buffer.write(image.file.read())

    logger.info(f"File saved to disk, size: {os.path.getsize(temp_file_path)} bytes")

    # Apply watermark to images only (not videos)
    if ext in ["jpg", "jpeg", "png"]:
        logger.info("Applying watermark...")
        apply_watermark(temp_file_path)

    try:
        upload = S3FileUploader(temp_file_path)
        image_url = upload.upload()
        logger.info(f"Successfully uploaded to S3: {image_url}")
    except S3UploaderError as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(status_code=500,
                            detail="Unable to upload image to AWS S3 Bucket")

    os.remove(temp_file_path)

    logger.info("Upload completed successfully")
    logger.info("=" * 50)

    return {"data": image_url}
