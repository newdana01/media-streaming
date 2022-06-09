import logging
import boto3
from botocore.exceptions import ClientError
from botocore.signers import CloudFrontSigner
import os, datetime
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner

logger = logging.getLogger(__name__)

class VideoUploader:
    def __init__(self, client, bucket:str) -> None:
        self.client = client
        self.bucket = bucket

    def generate_presigned_url(self, key:str, expires_in:int) -> str:
        try:
            presigned_url = self.client.generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in
            )
        except ClientError:
            logger.exception(f'Couldn\'t get a presigned URL for client method')
            raise
        return presigned_url

class CloudFrontTrustedSigner:
    def __init__(self) -> None:
        load_dotenv()
        self.expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        self.key_id = os.getenv('PUBLIC_KEY_ID')
        self.private_key_path = os.getenv('PRIVATE_KEY_PATH')

    def rsa_signer(self, message):
        with open(self.private_key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

    def generate_signed_url(self, url) -> str:
        cloudfront_signer = CloudFrontSigner(self.key_id, self.rsa_signer)
        signed_url = cloudfront_signer.generate_presigned_url(
            url, date_less_than=self.expire_date
            )
        
        return signed_url
