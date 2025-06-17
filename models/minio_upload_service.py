from odoo import models
from minio import Minio
from io import BytesIO

class MinIOUploadService(models.AbstractModel):
    _name = 'minio.upload.service'
    _description = 'MinIO Upload Service'

    def upload_file(self, filename, file_content):
        client = Minio(
            "localhost:9000",  # ganti dengan domain/IP MinIO-mu
            access_key="7THu6x4zIquDHvO4rSEg",
            secret_key="iypsOpwgZETG8EOiu5h8BHUVfRGmLlFtypOyrfCq",
            secure=False
        )
        bucket_name = "surat-pkwt"

        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        content_bytes = BytesIO(file_content)

        client.put_object(
            bucket_name,
            filename,
            data=content_bytes,
            length=len(file_content),
            content_type='application/pdf'
        )

        return f"http://localhost:9001//{bucket_name}/{filename}"
