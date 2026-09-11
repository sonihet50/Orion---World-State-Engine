import os
import uuid
from pathlib import Path
from typing import Optional
from app.config.settings import settings

def ensure_storage_dir(subfolder: Optional[str] = None) -> Path:
    base_dir = Path(settings.STORAGE_DIR)
    if subfolder:
        target_dir = base_dir / subfolder
    else:
        target_dir = base_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir

def save_file_content(content: bytes, filename: str, subfolder: str = "manuscripts") -> str:
    target_dir = ensure_storage_dir(subfolder)
    safe_name = f"{uuid.uuid4()}_{Path(filename).name}"
    file_path = target_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path.resolve())

def read_file_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def delete_file(file_path: str) -> bool:
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
    except Exception:
        pass
    return False
