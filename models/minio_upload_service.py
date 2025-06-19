from odoo import models
from minio import Minio
from io import BytesIO
from odoo.exceptions import UserError
from odoo.tools.translate import _


class MinIOUploadService(models.AbstractModel):
    _name = 'minio.upload.service'
    _description = 'MinIO Upload Service'

    def upload_file(self, filename, file_content):
        try:
            # Koneksi ke MinIO
            client = Minio(
                "cs3.ssmindonesia.com",
                access_key="VkNYbNVpLCw8AwOWngz7",
                secret_key="IILA5zElrEAa7Cpa4KZeaUUusRUP0QkqoAJIjZeA",
                secure=True
            )
        except Exception as e:
            raise UserError(_("Gagal konek ke server MinIO: %s") % str(e))

        bucket_name = "surat-pkwt"
        content_bytes = BytesIO(file_content)

        try:
            # Upload langsung tanpa cek bucket
            client.put_object(
                bucket_name=bucket_name,
                object_name=filename,
                data=content_bytes,
                length=len(file_content),
                content_type='application/pdf'
            )
        except Exception as e:
            raise UserError(_("Gagal mengunggah file ke MinIO: %s") % str(e))

        return f"https://cs3.ssmindonesia.com/{bucket_name}/{filename}"