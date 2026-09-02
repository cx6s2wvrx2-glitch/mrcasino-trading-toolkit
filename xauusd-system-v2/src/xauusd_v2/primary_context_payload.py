from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PrimaryImageEvidence:
    path: str
    mime_type: str
    sha256: str
    size_bytes: int

    @classmethod
    def from_path(cls, path: str | Path, *, mime_type: str) -> "PrimaryImageEvidence":
        file_path = Path(path)
        normalized_mime = mime_type.strip().lower()
        if not normalized_mime.startswith("image/"):
            raise ValueError("primary image evidence requires an image/* MIME type")
        if not file_path.is_file():
            raise FileNotFoundError(str(file_path))
        payload = file_path.read_bytes()
        if not payload:
            raise ValueError("primary image evidence cannot be empty")
        return cls(
            path=str(file_path.resolve()),
            mime_type=normalized_mime,
            sha256=hashlib.sha256(payload).hexdigest(),
            size_bytes=len(payload),
        )

    def verify(self) -> None:
        file_path = Path(self.path)
        if not file_path.is_file():
            raise FileNotFoundError(self.path)
        payload = file_path.read_bytes()
        if len(payload) != self.size_bytes:
            raise ValueError("primary image evidence size changed after resolution")
        if hashlib.sha256(payload).hexdigest() != self.sha256:
            raise ValueError("primary image evidence hash changed after resolution")


@dataclass(frozen=True, slots=True)
class PrimaryContextPayload:
    text: str = ""
    images: tuple[PrimaryImageEvidence, ...] = ()

    def normalized(self) -> "PrimaryContextPayload":
        text = self.text.strip()
        images = tuple(self.images)
        if not text and not images:
            raise ValueError("primary context requires source text or source images")
        for image in images:
            image.verify()
        return PrimaryContextPayload(text=text, images=images)
