import mimetypes
import os
import uuid

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseStorage(Storage):
    def __init__(self):
        self.base_url = settings.SUPABASE_URL.rstrip("/")
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self.service_key = settings.SUPABASE_SERVICE_KEY

    def _headers(self, content_type=None):
        headers = {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _object_url(self, name):
        return f"{self.base_url}/storage/v1/object/{self.bucket}/{name}"

    def _save(self, name, content):
        name = name.replace("\\", "/")
        content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        content.seek(0)
        data = content.read()

        response = requests.post(
            self._object_url(name),
            headers={**self._headers(content_type), "x-upsert": "true"},
            data=data,
            timeout=120,
        )
        if response.status_code not in (200, 201):
            raise IOError(
                f"Supabase upload failed ({response.status_code}): {response.text}"
            )
        return name

    def _open(self, name, mode="rb"):
        response = requests.get(self._object_url(name), headers=self._headers(), timeout=60)
        response.raise_for_status()
        return ContentFile(response.content, name=name)

    def exists(self, name):
        response = requests.head(self._object_url(name), headers=self._headers(), timeout=30)
        return response.status_code == 200

    def url(self, name):
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{name}"

    def size(self, name):
        response = requests.head(self._object_url(name), headers=self._headers(), timeout=30)
        return int(response.headers.get("Content-Length", 0))

    def delete(self, name):
        requests.delete(self._object_url(name), headers=self._headers(), timeout=30)

    def get_available_name(self, name, max_length=None):
        base, ext = os.path.splitext(name)
        return f"{base}-{uuid.uuid4().hex[:8]}{ext}"