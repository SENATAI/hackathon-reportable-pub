import aioboto3
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from typing_extensions import Self
from types_aiobotocore_s3 import S3Client

class S3ClientFactory:
    def __init__(
        self: Self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "us-east-1"
    ):
        self._endpoint_url = endpoint_url
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._region_name = region_name
        self._session = aioboto3.Session()

    @asynccontextmanager
    async def get_client(self: Self) -> AsyncGenerator[S3Client, None]:
        client = self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._region_name
        )
        try:
            async with client as c:
                yield c
        except Exception:
            raise