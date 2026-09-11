import hashlib
import uuid

def generate_uuid() -> str:
    """Generates a random UUID string."""
    return str(uuid.uuid4())

def compute_sha256(content: str) -> str:
    """Computes the SHA256 hex digest of a string or text content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def compute_file_sha256(file_bytes: bytes) -> str:
    """Computes the SHA256 hex digest of raw bytes."""
    return hashlib.sha256(file_bytes).hexdigest()
