"""Media library CRUD, upload/download, folders."""
import json
import mimetypes
import os
import uuid as _uuid

FOLDER_IMAGES_DEFAULT = 355995  # per-account; re-derive via get_categories(4)
FOLDER_VIDEOS_DEFAULT = 355994


class LibraryMixin:
    FOLDER_IMAGES = FOLDER_IMAGES_DEFAULT
    FOLDER_VIDEOS = FOLDER_VIDEOS_DEFAULT

    # ---------- reads ----------

    def categories(self, library_id=4):
        return self.get(f"/library/get_categories/{library_id}")

    def media_list(self, category_id, limit=50, page=1, query=""):
        return self.get(
            f"/api/library/get_media/4?categoryId={category_id}&page={page}"
            f"&start=0&limit={limit}&query={query}&orderBy=id&orderDir=desc&filter="
        )["results"]

    def media_item(self, media_id):
        return self.get(f"/library/get_media_item/{media_id}")

    # ---------- item CRUD (all writes fire ONCE) ----------

    def delete_item(self, media_id):
        return self.delete(f"/library/delete_item/{media_id}")

    def delete_items(self, ids):
        return self.post("/library/delete_items", json_body={"ids": list(ids)})

    def rename_item(self, media_id, name):
        return self.post(f"/library/edit_item/{media_id}", {"name": name})

    def move_item(self, media_id, category_id):
        return self.post(f"/library/move_item/{media_id}", {"categoryId": category_id})

    def move_items(self, ids, category_id):
        return self.post("/library/move_items",
                         json_body={"ids": list(ids), "categoryId": category_id})

    def copy_item(self, media_id, category_id):
        return self.post(f"/library/copy_item/{media_id}", {"categoryId": category_id})

    def share_item(self, media_id):
        return self.post(f"/library/share_item/{media_id}")

    def download_item(self, media_id, dest):
        url = f"{BASE_LIBRARY_DOWNLOAD}/{media_id}"
        return self.download(url, dest)

    # ---------- folders ----------

    def add_category(self, name, library_id=4):
        return self.post(f"/library/add_category/{library_id}", {"categoryName": name})

    def rename_category(self, category_id, new_name):
        return self.post(f"/library/rename_category/{category_id}", {"new_name": new_name})

    def delete_category(self, category_id):
        return self.post(f"/library/delete_category/{category_id}")

    # ---------- upload / download ----------

    def upload_file(self, file_path, category_id, library_id=4):
        """Multipart upload to a library folder (Dropzone-style)."""
        name = os.path.basename(file_path)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        boundary = f"----vx{_uuid.uuid4().hex}"
        with open(file_path, "rb") as f:
            payload = f.read()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n").encode() + body_bytes(payload, boundary)
        import urllib.request
        req = urllib.request.Request(
            f"{_base()}/library/upload/{library_id}?categoryId={category_id}",
            data=body, headers=self.auth.headers(
                content_type=f"multipart/form-data; boundary={boundary}"),
            method="POST")
        with self._open(req, 300) as r:
            return json.loads(r.read().decode())

    def download_media(self, media, dest):
        """Download a media item: prefers its CDN mediaPath, else /library/download."""
        url = media.get("mediaPath") or media.get("path")
        if not url:
            url = f"{_base()}/library/download/{media['id']}"
        return self.download(url, dest)


BASE_LIBRARY_DOWNLOAD = "https://app.videoexpress.ai/library/download"


def _base():
    from .http import BASE
    return BASE


def body_bytes(payload, boundary):
    return payload + f"\r\n--{boundary}--\r\n".encode()
