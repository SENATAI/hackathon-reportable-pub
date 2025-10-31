import asyncio
from fastapi import UploadFile
from botocore.exceptions import ClientError
import logging
from typing import Protocol, cast
from typing_extensions import Self
from types_aiobotocore_s3 import S3Client
from ....core.clients.s3_client import S3ClientFactory


logger = logging.getLogger(__name__)


class FileServiceProtocol(Protocol):
    async def upload(self: Self, path: str, file: UploadFile) -> bool:
        ...
    
    async def get_url(self: Self, path: str) -> str:
         ...
    
    async def delete(self: Self, path: str) -> bool:
         ...

    async def upload_html(self: Self, path: str, html_text: str) -> bool:
        ...
    
    async def upload_content(self: Self, path: str, content: bytes, content_type: str = "application/octet-stream") -> bool:
        ...

    async def upload_batch(self: Self, files: list[tuple[str, UploadFile]]) -> list[bool]:
        ...


class S3FileService(FileServiceProtocol):
    def __init__(self: Self, client_factory: S3ClientFactory, bucket_name: str, real_url: str, url_to_change: str):
        self.client_factory = client_factory
        self.bucket_name = bucket_name
        self.real_url = real_url
        self.url_to_change = url_to_change
        self._bucket_checked = False

    async def _ensure_bucket_exists(self) -> None:
        """Ленивая проверка и создание bucket'а"""
        if self._bucket_checked:
            return
            
        try:
            async with self.client_factory.get_client() as client:
                s3_client = cast(S3Client, client)
                try:
                    await s3_client.head_bucket(Bucket=self.bucket_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        await s3_client.create_bucket(Bucket=self.bucket_name)
                        logger.info(f"Bucket {self.bucket_name} created")
                    else:
                        raise
            self._bucket_checked = True
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise

    async def upload(self: Self, path: str, file: UploadFile) -> bool:
        await self._ensure_bucket_exists()
        try:
            contents = await file.read()
            content_type = file.content_type or "application/octet-stream"
            
            # Используем существующий метод upload_content
            return await self._upload_content(path, contents, content_type)
            
        except Exception as e:
            logger.error(f"Failed to upload file {path}: {e}")
            return False

    async def upload_content(self: Self, path: str, content: bytes, content_type: str = "application/octet-stream") -> bool:
        await self._ensure_bucket_exists()
        return await self._upload_content(path, content, content_type)


    async def _upload_content(self: Self, path: str, content: bytes, content_type: str = "application/octet-stream") -> bool:
        try:
            async with self.client_factory.get_client() as client:
                s3_client = cast(S3Client, client)
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=path,
                    Body=content,
                    ContentType=content_type
                )
            logger.info(f"File uploaded successfully: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file {path}: {e}")
            return False
        
    async def upload_batch(self: Self, files: list[tuple[str, UploadFile]]) -> list[bool]:
        """
        Загрузка пачки файлов параллельно
        
        Args:
            files: Список кортежей (path, file)
            
        Returns:
            Список результатов загрузки (True/False для каждого файла)
        """
        await self._ensure_bucket_exists()
        
        # Создаем задачи для параллельной загрузки
        tasks = [self.upload(path, file) for path, file in files]
        
        # Выполняем все загрузки параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обрабатываем возможные исключения
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch upload error: {result}")
                processed_results.append(False)
            else:
                processed_results.append(result)
        
        return processed_results


    async def upload_html(self: Self, path: str, html_text: str) -> bool:
        await self._ensure_bucket_exists()
        try:
            async with self.client_factory.get_client() as client:
                s3_client = cast(S3Client, client)
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=path,
                    Body=html_text.encode("utf-8"),
                    ContentType="text/html; charset=utf-8"
                )
            logger.info(f"HTML file uploaded successfully: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload HTML file {path}: {e}")
            return False

    async def get_url(self: Self, path: str) -> str:
        # TODO: Redis чтобы каждый раз не генерировать новую ссылку
        await self._ensure_bucket_exists()
        try:
            async with self.client_factory.get_client() as client:
                s3_client = cast(S3Client, client)

                # Генерируем presigned URL на 30 минут
                url = await s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': path},
                    ExpiresIn=1800  # 30 минут
                )
            
            new_url = url.replace(
                self.real_url, 
                self.url_to_change
            )
            return new_url
            
        except Exception as e:
            logger.error(f"Failed to generate URL for {path}: {e}")
            raise

    async def delete(self: Self, path: str) -> bool:
        await self._ensure_bucket_exists()
        try:
            async with self.client_factory.get_client() as client:
                s3_client = cast(S3Client, client)

                
                # Проверяем существование объекта
                try:
                    await s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=path
                    )
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        logger.warning(f"File not found for deletion: {path}")
                        return False
                    raise
                
                # Удаляем объект
                await s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=path
                )
                
            logger.info(f"File deleted successfully: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return False