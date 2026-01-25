import os
from pathlib import Path

from app.core.config import get_settings


class FileManager:
    def __init__(self) -> None:
        settings = get_settings()
        self._root = Path(settings.files_root).resolve()

    def _abs(self, relative_path: str) -> Path:
        safe = relative_path.replace("\u202A", " ").strip().lstrip("/\\")
        return self._root / safe

    def exists(self, relative_path: str) -> bool:
        return self._abs(relative_path).exists()

    def open_read(self, relative_path: str):
        path = self._abs(relative_path)
        if not path.exists():
            return None
        return path.open("rb")

    def save(self, relative_path: str, content: bytes) -> None:
        path = self._abs(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(content)

    def delete(self, relative_path: str) -> None:
        path = self._abs(relative_path)
        if path.exists():
            try:
                os.remove(path)
            except OSError:
                pass
