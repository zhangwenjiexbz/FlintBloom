from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.db.models import Checkpoint, CheckpointBlob, CheckpointWrite


class BaseDatabaseAdapter(ABC):
    """
    Abstract base class for database adapters
    Provides unified interface for different database types
    """

    def __init__(self, session: Session):
        self.session = session

    # ============= Thread Operations =============

    def get_threads(
        self,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "thread_id",
        order: str = "desc"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get list of threads with pagination

        Returns:
            Tuple of (thread_list, total_count)
        """
        query = self.session.query(Checkpoint.thread_id).distinct()

        # Get total count
        total = query.count()

        # Apply ordering and pagination
        if order == "desc":
            query = query.order_by(Checkpoint.thread_id.desc())
        else:
            query = query.order_by(Checkpoint.thread_id.asc())

        threads = query.limit(limit).offset(offset).all()

        # Get additional info for each thread
        thread_list = []
        for (thread_id,) in threads:
            checkpoint_count = self.session.query(Checkpoint).filter(
                Checkpoint.thread_id == thread_id
            ).count()

            latest_checkpoint = self.session.query(Checkpoint).filter(
                Checkpoint.thread_id == thread_id
            ).order_by(Checkpoint.checkpoint_id.desc()).first()

            thread_list.append({
                "thread_id": thread_id,
                "checkpoint_count": checkpoint_count,
                "latest_checkpoint_id": latest_checkpoint.checkpoint_id if latest_checkpoint else None,
            })

        return thread_list, total

    # ============= Checkpoint Operations =============

    def get_checkpoints_by_thread(
        self,
        thread_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Checkpoint], int]:
        """Get checkpoints for a specific thread"""
        query = self.session.query(Checkpoint).filter(
            Checkpoint.thread_id == thread_id
        )

        total = query.count()

        checkpoints = query.order_by(
            Checkpoint.checkpoint_id.desc()
        ).limit(limit).offset(offset).all()

        return checkpoints, total

    def get_checkpoint(
        self,
        thread_id: str,
        checkpoint_id: str,
        checkpoint_ns: str = ""
    ) -> Optional[Checkpoint]:
        """Get a specific checkpoint"""
        return self.session.query(Checkpoint).filter(
            Checkpoint.thread_id == thread_id,
            Checkpoint.checkpoint_id == checkpoint_id,
            Checkpoint.checkpoint_ns == checkpoint_ns
        ).first()

    def get_checkpoint_with_parent_chain(
        self,
        thread_id: str,
        checkpoint_id: str,
        checkpoint_ns: str = ""
    ) -> List[Checkpoint]:
        """Get checkpoint and all its parents"""
        checkpoints = []
        current_id = checkpoint_id

        while current_id:
            checkpoint = self.get_checkpoint(thread_id, current_id, checkpoint_ns)
            if not checkpoint:
                break

            checkpoints.append(checkpoint)
            current_id = checkpoint.parent_checkpoint_id

        return checkpoints

    # ============= Blob Operations =============

    def get_checkpoint_blobs(
        self,
        thread_id: str,
        checkpoint_ns: str = "",
        checkpoint_ns_hash: Optional[bytes] = None
    ) -> List[CheckpointBlob]:
        """Get all blobs for a checkpoint"""
        query = self.session.query(CheckpointBlob).filter(
            CheckpointBlob.thread_id == thread_id,
            CheckpointBlob.checkpoint_ns == checkpoint_ns
        )

        if checkpoint_ns_hash:
            query = query.filter(CheckpointBlob.checkpoint_ns_hash == checkpoint_ns_hash)

        return query.all()

    def get_checkpoint_blob(
        self,
        thread_id: str,
        channel: str,
        version: str,
        checkpoint_ns: str = "",
        checkpoint_ns_hash: Optional[bytes] = None
    ) -> Optional[CheckpointBlob]:
        """Get a specific blob"""
        query = self.session.query(CheckpointBlob).filter(
            CheckpointBlob.thread_id == thread_id,
            CheckpointBlob.channel == channel,
            CheckpointBlob.version == version,
            CheckpointBlob.checkpoint_ns == checkpoint_ns
        )

        if checkpoint_ns_hash:
            query = query.filter(CheckpointBlob.checkpoint_ns_hash == checkpoint_ns_hash)

        return query.first()

    # ============= Write Operations =============

    def get_checkpoint_writes(
        self,
        thread_id: str,
        checkpoint_id: str,
        checkpoint_ns: str = ""
    ) -> List[CheckpointWrite]:
        """Get all writes for a checkpoint"""
        return self.session.query(CheckpointWrite).filter(
            CheckpointWrite.thread_id == thread_id,
            CheckpointWrite.checkpoint_id == checkpoint_id,
            CheckpointWrite.checkpoint_ns == checkpoint_ns
        ).order_by(CheckpointWrite.idx).all()

    def get_checkpoint_writes_by_task(
        self,
        thread_id: str,
        checkpoint_id: str,
        task_id: str,
        checkpoint_ns: str = ""
    ) -> List[CheckpointWrite]:
        """Get writes for a specific task"""
        return self.session.query(CheckpointWrite).filter(
            CheckpointWrite.thread_id == thread_id,
            CheckpointWrite.checkpoint_id == checkpoint_id,
            CheckpointWrite.task_id == task_id,
            CheckpointWrite.checkpoint_ns == checkpoint_ns
        ).order_by(CheckpointWrite.idx).all()

    # ============= Database-specific Operations =============

    @abstractmethod
    def optimize_query(self, query):
        """Apply database-specific query optimizations"""
        pass

    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """Get database-specific information"""
        pass
