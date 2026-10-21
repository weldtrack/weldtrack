from io import BytesIO
import json
from pathlib import Path
import socket

from minio import Minio

from app.core.config import settings

LOCAL_UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"

client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


def _is_minio_reachable() -> bool:
    host_port = settings.MINIO_ENDPOINT.split("://")[-1].split("/")[0]
    if ":" in host_port:
        host, port_str = host_port.rsplit(":", 1)
        port = int(port_str)
    else:
        host = host_port
        port = 443 if settings.MINIO_SECURE else 9000
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


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
    if _is_minio_reachable():
        try:
            ensure_bucket()
            client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                BytesIO(data),
                len(data),
                content_type=content_type,
            )
            return object_name
        except Exception:
            pass
    target_path = LOCAL_UPLOADS_DIR / object_name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(data)
    return f"local:{object_name}"


def public_url(object_name: str) -> str:
    if object_name.startswith("local:"):
        rel = object_name.removeprefix("local:").lstrip("/")
        return f"/uploads/{rel}"
    local_candidate = LOCAL_UPLOADS_DIR / object_name.lstrip("/")
    if local_candidate.is_file():
        return f"/uploads/{object_name.lstrip('/')}"
    base_url = settings.MINIO_PUBLIC_URL.rstrip("/")
    return f"{base_url}/{settings.MINIO_BUCKET}/{object_name}"

