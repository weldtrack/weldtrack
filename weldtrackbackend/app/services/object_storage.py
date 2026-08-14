from io import BytesIO
import json

from minio import Minio

from app.core.config import settings

client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


def ensure_bucket() -> None:
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)
    client.set_bucket_policy(
        settings.MINIO_BUCKET,
        json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"],
                    }
                ],
            }
        ),
    )


def upload(object_name: str, data: bytes, content_type: str) -> str:
    ensure_bucket()
    client.put_object(
        settings.MINIO_BUCKET,
        object_name,
        BytesIO(data),
        len(data),
        content_type=content_type,
    )
    return object_name


def public_url(object_name: str) -> str:
    base_url = settings.MINIO_PUBLIC_URL.rstrip("/")
    return f"{base_url}/{settings.MINIO_BUCKET}/{object_name}"
