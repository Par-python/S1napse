import boto3
from botocore.client import Config
from app.config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4")
    )

def generate_presigned_put(s3_key: str, expires_in: int = 600):
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": s3_key, "ContentType": "application/gzip"},
        ExpiresIn=expires_in,
    )
