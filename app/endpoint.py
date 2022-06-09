import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel

from uploader import VideoUploader, CloudFrontTrustedSigner
from db_config import conn

router = FastAPI()

class ReviewCreateObject(BaseModel):
    user_id: int
    file_name: str
    req_url: str = None

@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
)
def post_upload_review_videos(review_obj: ReviewCreateObject):
    load_dotenv()

    client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRETKEY_ACCESS_KEY'),
        region_name=os.getenv('REGION_NAME')
        )

    videoUplodader = VideoUploader(client, os.getenv('BUCKET_NAME'))

    presigned_url = videoUplodader.generate_presigned_url(review_obj.file_name, 120)
    
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    REGION_NAME = os.getenv('REGION_NAME')

    original_file_path = f'https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{review_obj.user_id}-{datetime.now().year}-{review_obj.file_name}'
    ### 디비에 일차로 저장해야함!
    conn.execute(
        f'INSERT INTO review_videos (user_id, file_url) VALUES ({review_obj.user_id}, \'{original_file_path}\')'
        )

    return {"presigned_url": presigned_url}

@router.post(
    "/upload/streaming-url",
    status_code=status.HTTP_200_OK
    )
def post_streaming_url():
    # url update
    return {"message": "SUCCESS"}

@router.post(
    "/upload/signed-url",
    status_code=status.HTTP_200_OK
    )
def post_signed_url(review_obj: ReviewCreateObject):
    cfSinger = CloudFrontTrustedSigner()
    signed_url = cfSinger.generate_signed_url(url=review_obj.req_url)

    return {'message': 'SUCCESS', 'signed_url': signed_url}