from sqlalchemy import Column, String, Integer, LargeBinary, JSON, Index, text
from sqlalchemy.dialects.mysql import LONGBLOB
from app.core.database import Base


class CheckpointBlob(Base):
    """
    Stores binary data for checkpoint channels
    """
    __tablename__ = "checkpoint_blobs"

    thread_id = Column(String(150), primary_key=True, nullable=False)
    checkpoint_ns = Column(String(2000), primary_key=True, nullable=False, default="", server_default=text("''"))
    channel = Column(String(150), primary_key=True, nullable=False)
    version = Column(String(150), primary_key=True, nullable=False)
    type = Column(String(150), nullable=False)
    blob = Column(LargeBinary, nullable=True)  # LONGBLOB in MySQL
    checkpoint_ns_hash = Column(LargeBinary(16), primary_key=True, nullable=False)

    __table_args__ = (
        Index("checkpoint_blobs_thread_id_idx", "thread_id"),
    )

    def __repr__(self):
        return f"<CheckpointBlob(thread_id={self.thread_id}, channel={self.channel}, version={self.version})>"


class CheckpointWrite(Base):
    """
    Stores write operations for checkpoints
    """
    __tablename__ = "checkpoint_writes"

    thread_id = Column(String(150), primary_key=True, nullable=False)
    checkpoint_ns = Column(String(2000), primary_key=True, nullable=False, default="", server_default=text("''"))
    checkpoint_id = Column(String(150), primary_key=True, nullable=False)
    task_id = Column(String(150), primary_key=True, nullable=False)
    idx = Column(Integer, primary_key=True, nullable=False)
    channel = Column(String(150), nullable=False)
    type = Column(String(150), nullable=True)
    blob = Column(LargeBinary, nullable=False)  # LONGBLOB in MySQL
    checkpoint_ns_hash = Column(LargeBinary(16), primary_key=True, nullable=False)
    task_path = Column(String(2000), nullable=False, default="", server_default=text("''"))

    __table_args__ = (
        Index("checkpoint_writes_thread_id_idx", "thread_id"),
    )

    def __repr__(self):
        return f"<CheckpointWrite(thread_id={self.thread_id}, checkpoint_id={self.checkpoint_id}, task_id={self.task_id})>"


class Checkpoint(Base):
    """
    Main checkpoint metadata and state
    """
    __tablename__ = "checkpoints"

    thread_id = Column(String(150), primary_key=True, nullable=False)
    checkpoint_ns = Column(String(2000), primary_key=True, nullable=False, default="", server_default=text("''"))
    checkpoint_id = Column(String(150), primary_key=True, nullable=False)
    parent_checkpoint_id = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    checkpoint = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict, server_default=text("'{}'"))
    checkpoint_ns_hash = Column(LargeBinary(16), primary_key=True, nullable=False)

    __table_args__ = (
        Index("checkpoints_thread_id_idx", "thread_id"),
        Index("checkpoints_checkpoint_id_idx", "checkpoint_id"),
    )

    def __repr__(self):
        return f"<Checkpoint(thread_id={self.thread_id}, checkpoint_id={self.checkpoint_id})>"


class CheckpointMigration(Base):
    """
    Tracks database schema migrations
    """
    __tablename__ = "checkpoint_migrations"

    v = Column(Integer, primary_key=True, nullable=False)

    def __repr__(self):
        return f"<CheckpointMigration(v={self.v})>"
