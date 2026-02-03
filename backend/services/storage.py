"""
Digest storage and retrieval module.
Manages persistence and querying of digest runs.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
from ..logging_config import get_logger

logger = get_logger(__name__)


class DigestMetadata(BaseModel):
    """Metadata about a digest run."""
    timestamp: str  # ISO 8601
    item_count: int
    path: str
    digest_id: str
    duration_seconds: Optional[float] = None


class DigestInfo(BaseModel):
    """Full digest information with metadata and content."""
    metadata: DigestMetadata
    items: List[dict]
    summary: Optional[str] = None


class DigestStorage:
    """Manages digest file storage and retrieval."""

    def __init__(self, storage_dir: str = "out"):
        """
        Initialize storage.

        Args:
            storage_dir: Directory for storing digests (default: 'out').
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_dir / "digest_history.json"
        logger.info(
            f"DigestStorage initialized at {self.storage_dir}",
            extra={"storage_dir": str(self.storage_dir), "component": "storage"},
        )

    def save_digest(
        self,
        items: List[dict],
        digest_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
    ) -> DigestMetadata:
        """
        Save a digest run.

        Args:
            items: List of digest items.
            digest_id: Optional custom digest ID (auto-generated if not provided).
            duration_seconds: Duration of digest generation in seconds.

        Returns:
            DigestMetadata for the saved digest.
        """
        timestamp = datetime.utcnow()
        if digest_id is None:
            digest_id = timestamp.strftime("%Y%m%d_%H%M%S")

        path = self.storage_dir / f"{digest_id}.json"

        try:
            # Save digest file
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"items": items}, f, indent=2)

            metadata = DigestMetadata(
                timestamp=timestamp.isoformat(),
                item_count=len(items),
                path=str(path),
                digest_id=digest_id,
                duration_seconds=duration_seconds,
            )

            # Update history
            self._append_to_history(metadata)

            logger.info(
                f"Digest saved: {digest_id}",
                extra={
                    "digest_id": digest_id,
                    "item_count": len(items),
                    "duration": duration_seconds,
                    "component": "storage",
                },
            )

            return metadata

        except Exception as e:
            logger.error(
                f"Failed to save digest: {str(e)}",
                extra={"digest_id": digest_id, "error": str(e), "component": "storage"},
                exc_info=True,
            )
            raise

    def get_digest(self, digest_id: str) -> Optional[DigestInfo]:
        """
        Retrieve a digest by ID.

        Args:
            digest_id: The digest ID to retrieve.

        Returns:
            DigestInfo or None if not found.
        """
        path = self.storage_dir / f"{digest_id}.json"

        try:
            if not path.exists():
                logger.warning(
                    f"Digest not found: {digest_id}",
                    extra={"digest_id": digest_id, "component": "storage"},
                )
                return None

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Get metadata from history
            history = self._load_history()
            metadata = None
            for entry in history:
                if entry.get("digest_id") == digest_id:
                    metadata = DigestMetadata(**entry)
                    break

            if metadata is None:
                # Fallback: create minimal metadata
                metadata = DigestMetadata(
                    timestamp=datetime.utcnow().isoformat(),
                    item_count=len(data.get("items", [])),
                    path=str(path),
                    digest_id=digest_id,
                )

            logger.debug(
                f"Retrieved digest: {digest_id}",
                extra={"digest_id": digest_id, "component": "storage"},
            )

            return DigestInfo(metadata=metadata, items=data.get("items", []))

        except Exception as e:
            logger.error(
                f"Failed to retrieve digest: {str(e)}",
                extra={"digest_id": digest_id, "error": str(e), "component": "storage"},
                exc_info=True,
            )
            return None

    def list_digests(
        self,
        limit: int = 10,
        offset: int = 0,
        days: Optional[int] = None,
    ) -> List[DigestMetadata]:
        """
        List recent digests.

        Args:
            limit: Maximum number of digests to return (default: 10).
            offset: Offset for pagination (default: 0).
            days: Filter to last N days (optional).

        Returns:
            List of DigestMetadata sorted by timestamp (newest first).
        """
        try:
            history = self._load_history()

            # Filter by days if specified
            if days is not None:
                cutoff = datetime.utcnow() - timedelta(days=days)
                history = [
                    entry
                    for entry in history
                    if datetime.fromisoformat(entry["timestamp"]) > cutoff
                ]

            # Sort by timestamp (newest first)
            history.sort(
                key=lambda x: x["timestamp"], reverse=True
            )

            # Paginate
            paginated = history[offset : offset + limit]

            # Convert to DigestMetadata
            digests = [DigestMetadata(**entry) for entry in paginated]

            logger.debug(
                f"Listed {len(digests)} digests (offset={offset}, limit={limit})",
                extra={
                    "count": len(digests),
                    "offset": offset,
                    "limit": limit,
                    "component": "storage",
                },
            )

            return digests

        except Exception as e:
            logger.error(
                f"Failed to list digests: {str(e)}",
                extra={"error": str(e), "component": "storage"},
                exc_info=True,
            )
            return []

    def delete_digest(self, digest_id: str) -> bool:
        """
        Delete a digest.

        Args:
            digest_id: The digest ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        path = self.storage_dir / f"{digest_id}.json"

        try:
            if not path.exists():
                logger.warning(
                    f"Digest not found for deletion: {digest_id}",
                    extra={"digest_id": digest_id, "component": "storage"},
                )
                return False

            path.unlink()

            # Remove from history
            history = self._load_history()
            history = [h for h in history if h.get("digest_id") != digest_id]
            self._save_history(history)

            logger.info(
                f"Digest deleted: {digest_id}",
                extra={"digest_id": digest_id, "component": "storage"},
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to delete digest: {str(e)}",
                extra={"digest_id": digest_id, "error": str(e), "component": "storage"},
                exc_info=True,
            )
            return False

    def _append_to_history(self, metadata: DigestMetadata) -> None:
        """Append metadata to history file."""
        history = self._load_history()
        history.append(metadata.dict())
        self._save_history(history)

    def _load_history(self) -> List[dict]:
        """Load history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(
                f"Failed to load history: {str(e)}",
                extra={"error": str(e), "component": "storage"},
            )
            return []

    def _save_history(self, history: List[dict]) -> None:
        """Save history to file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(
                f"Failed to save history: {str(e)}",
                extra={"error": str(e), "component": "storage"},
                exc_info=True,
            )


# Global storage instance
_storage: Optional[DigestStorage] = None


def get_storage(storage_dir: str = "out") -> DigestStorage:
    """
    Get or create the global DigestStorage instance.

    Args:
        storage_dir: Directory for storing digests.

    Returns:
        DigestStorage instance.
    """
    global _storage

    if _storage is None:
        _storage = DigestStorage(storage_dir)

    return _storage
