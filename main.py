import os

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.params import Header
from fastapi.middleware.cors import CORSMiddleware

import settings
import requests

from aws.s3 import S3FileUploader, S3UploaderError
from utils.files import sanitize_filename

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

    response = requests.post(url, json={"query": query}, headers=headers)
    response = response.json()

    data = response.get("data")

    me = data.get("me")

    if not me:
        raise TokenError("Unable to authenticate with provided token")


@app.post("/uploadImage")
async def upload_image(
        image: UploadFile,
        Authorization: str = Header(...),
):
    allowed_extensions = ["jpg", "jpeg", "png"]
    ext = image.filename.split(".")[-1]

    try:
        verify_token(Authorization)
    except TokenError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400,
                            detail="File type is not supported")

    temp_file_path = str(os.path.join(
        settings.DOWNLOADS_FOLDER,
        sanitize_filename(image.filename)
    ))

    with open(temp_file_path, "wb+") as buffer:
        buffer.write(image.file.read())

    try:
        upload = S3FileUploader(temp_file_path)
        image_url = upload.upload()
    except S3UploaderError:
        raise HTTPException(status_code=500,
                            detail="Unable to upload image to AWS S3 Bucket")

    os.remove(temp_file_path)

    return {"data": image_url}
