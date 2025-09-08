import os
import shutil
from datetime import datetime
from typing import Tuple

from flask import current_app
from ..utils import ensure_dir, compute_checksum


class StorageService:
    """
    Handles file storage under STORAGE_ROOT using per-user and per-document/version folders.
    """

    def __init__(self):
        self.root = current_app.config["STORAGE_ROOT"]
        ensure_dir(self.root)

    def _doc_dir(self, user_id: int, document_id: int) -> str:
        path = os.path.join(self.root, f"user_{user_id}", f"doc_{document_id}")
        ensure_dir(path)
        return path

    # PUBLIC_INTERFACE
    def save_new_version(self, user_id: int, document_id: int, filename: str, file_stream) -> Tuple[str, int, str]:
        """Save a new file version for a document.

        Parameters:
        - user_id: Owner user id.
        - document_id: Document id to which this version belongs.
        - filename: Original filename provided by the client.
        - file_stream: Binary stream of the file.

        Returns:
        - tuple(relative_path: str, size_bytes: int, checksum: str)
        """
        now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        base_dir = self._doc_dir(user_id, document_id)
        safe_name = f"{now}__{os.path.basename(filename)}"
        abs_path = os.path.join(base_dir, safe_name)
        with open(abs_path, "wb") as out:
            shutil.copyfileobj(file_stream, out)
        size = os.path.getsize(abs_path)
        checksum = compute_checksum(abs_path)
        rel_path = os.path.relpath(abs_path, self.root)
        return rel_path, size, checksum

    # PUBLIC_INTERFACE
    def get_absolute_path(self, relative_path: str) -> str:
        """Return absolute on-disk path for a stored file relative path.

        Parameters:
        - relative_path: Path relative to STORAGE_ROOT returned by save_new_version.

        Returns:
        - str: Absolute filesystem path.
        """
        return os.path.join(self.root, relative_path)
