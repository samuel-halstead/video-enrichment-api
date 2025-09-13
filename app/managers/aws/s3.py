from typing import Any

import boto3

from app.core.config import logger, settings


def _get_client():
    if len(settings.S3_PROFILE) > 0:
        session = boto3.Session(profile_name=settings.S3_PROFILE)
        return session.client("s3")
    return boto3.client("s3")


class S3Manager:
    def __init__(self):
        self._client = _get_client()

    @staticmethod
    def decode_path(object_path: str) -> tuple[str, str]:
        bucket = object_path.split("/")[0]
        key = object_path.replace(f"{bucket}/", "")
        return bucket, key

    @staticmethod
    def encode_path(bucket: str, key: str) -> str:
        return f"{bucket}/{key}"

    def exists(self, bucket: str, key: str) -> bool:
        try:
            self._client.head_object(
                Bucket=bucket,
                Key=key,
            )
        except self._client.exceptions.NoSuchKey:
            return False
        except self._client.exceptions.ClientError:
            return False

        return True

    def list_objects(self, bucket: str, prefix: str) -> list[dict[str, Any]]:
        response = self._client.list_objects(Bucket=bucket, Prefix=prefix)
        if "Contents" not in response:
            return []
        return response["Contents"]

    def upload_object(self, bucket: str, key: str, content: Any) -> bool:
        try:
            self._client.put_object(
                Body=content,
                Bucket=bucket,
                Key=key,
            )
            return True
        except Exception as err:
            logger.error(f"Error Uploading file {bucket}/{key}: {err}")
            return False

    def delete_objects(self, bucket: str, prefixes: list[str]) -> None:
        for prefix in prefixes:
            self._client.delete_object(
                Bucket=bucket,
                Key=prefix,
            )

    def delete_object(self, bucket: str, key: str) -> None:
        if not self.exists(bucket, key):
            return
        try:
            self._client.delete_object(
                Bucket=bucket,
                Key=key,
            )
        except Exception as err:
            logger.error(f"Error Deleting file {bucket}/{key}: {err}")
            return

    def download_object(self, bucket: str, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as err:
            logger.error(f"Error Downloading file {bucket}/{key}: {err}")
            return None


s3_manager = S3Manager()
