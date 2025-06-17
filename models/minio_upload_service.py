from odoo import models
from minio import Minio
from io import BytesIO
from odoo.exceptions import UserError


class MinIOUploadService(models.AbstractModel):
    _name = 'minio.upload.service'
    _description = 'MinIO Upload Service'

    def upload_file(self, filename, file_content):
        client = Minio(
            "localhost:9000",  # Ubah jika MinIO Anda di server lain
            access_key="7THu6x4zIquDHvO4rSEg",
            secret_key="iypsOpwgZETG8EOiu5h8BHUVfRGmLlFtypOyrfCq",
            secure=False
        )
        bucket_name = "surat-pkwt"

        # Buat bucket jika belum ada
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        content_bytes = BytesIO(file_content)

        try:
            client.put_object(
                bucket_name,
                filename,
                data=content_bytes,
                length=len(file_content),
                content_type='application/pdf'
            )
        except Exception as e:
            raise UserError(_("Gagal mengunggah file ke MinIO: %s") % str(e))

        # Hasil URL file
        return f"http://localhost:9001/{bucket_name}/{filename}"
