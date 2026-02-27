from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.db.schemas import (
    ThreadListResponse,
    CheckpointListResponse,
    TraceDetailResponse,
    ThreadInfo,
)
from app.db.adapters import get_adapter
from app.modules.offline.analyzer import CheckpointAnalyzer
from app.modules.offline.parser import CheckpointParser

router = APIRouter(prefix="/offline", tags=["Offline Analysis"])


def _convert_metadata_to_dict(metadata) -> dict:
    """
    Convert MetaData object to dictionary

    Handles LangGraph's MetaData objects which have attributes like:
    - source: str
    - writes: list
    - parents: dict
    - step: int
    """
    if metadata is None:
        return {}
    elif isinstance(metadata, dict):
        return metadata
    elif hasattr(metadata, '__dict__'):
        # It's a MetaData or similar object
        return {
            "source": getattr(metadata, 'source', None),
            "writes": getattr(metadata, 'writes', []),
            "parents": getattr(metadata, 'parents', {}),
            "step": getattr(metadata, 'step', None),
        }
    else:
        # Fallback: try to convert to dict
        try:
            return dict(metadata)
        except:
            return {}


def _bytes_to_hex(value) -> Optional[str]:
    """Convert bytes to hex string"""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


@router.get("/threads", response_model=ThreadListResponse)
async def list_threads(
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    order_by: str = Query(default="thread_id", regex="^(thread_id)$"),
    order: str = Query(default="desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    List all threads with pagination

    Args:
        limit: Maximum number of threads to return
        offset: Number of threads to skip
        order_by: Field to order by
        order: Sort order (asc or desc)
        db: Database session

    Returns:
        List of threads with metadata
    """
    adapter = get_adapter(db)
    threads, total = adapter.get_threads(limit, offset, order_by, order)

    thread_infos = [
        ThreadInfo(
            thread_id=t["thread_id"],
            checkpoint_count=t["checkpoint_count"],
            latest_checkpoint_id=t["latest_checkpoint_id"],
        )
        for t in threads
    ]

    return ThreadListResponse(
        threads=thread_infos,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/threads/{thread_id}/checkpoints", response_model=CheckpointListResponse)
async def list_checkpoints(
    thread_id: str,
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List checkpoints for a specific thread

    Args:
        thread_id: Thread identifier
        limit: Maximum number of checkpoints to return
        offset: Number of checkpoints to skip
        db: Database session

    Returns:
        List of checkpoints
    """
    from app.db.schemas import CheckpointSchema

    adapter = get_adapter(db)
    checkpoints_raw, total = adapter.get_checkpoints_by_thread(thread_id, limit, offset)

    # Convert Checkpoint objects to schemas, handling MetaData and bytes
    checkpoints = []
    for cp in checkpoints_raw:
        checkpoint_dict = {
            "thread_id": cp.thread_id,
            "checkpoint_ns": cp.checkpoint_ns,
            "checkpoint_id": cp.checkpoint_id,
            "parent_checkpoint_id": cp.parent_checkpoint_id,
            "type": cp.type,
            "checkpoint": cp.checkpoint,
            "metadata": _convert_metadata_to_dict(cp.metadata) if cp.metadata else {},
            "checkpoint_ns_hash": _bytes_to_hex(cp.checkpoint_ns_hash),
        }
        checkpoints.append(CheckpointSchema(**checkpoint_dict))

    return CheckpointListResponse(
        checkpoints=checkpoints,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/threads/{thread_id}/checkpoints/{checkpoint_id}/trace")
async def get_trace(
    thread_id: str,
    checkpoint_id: str,
    include_blobs: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    """
    Get execution trace for a specific checkpoint

    Args:
        thread_id: Thread identifier
        checkpoint_id: Checkpoint identifier
        checkpoint_ns: Checkpoint namespace
        include_blobs: Whether to include blob data
        db: Database session

    Returns:
        Trace graph with execution details
    """
    adapter = get_adapter(db)
    parser = CheckpointParser()

    # Get checkpoint
    checkpoint = adapter.get_checkpoint(thread_id, checkpoint_id,)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    # Get related data
    writes = adapter.get_checkpoint_writes(thread_id, checkpoint_id)
    blobs = None
    if include_blobs:
        blobs = adapter.get_checkpoint_blobs(thread_id)

    # Build trace graph
    trace_graph = parser.build_trace_graph(checkpoint, writes, blobs)

    # Get execution summary
    analyzer = CheckpointAnalyzer(db)
    summary = analyzer.analyze_checkpoint(thread_id, checkpoint_id)

    # Get checkpoint chain
    checkpoint_chain_raw = adapter.get_checkpoint_with_parent_chain(
        thread_id, checkpoint_id
    )

    # Convert Checkpoint objects to dicts, handling MetaData and bytes
    from app.db.schemas import CheckpointSchema
    checkpoint_chain = []
    for cp in checkpoint_chain_raw:
        # Convert to dict with proper metadata and bytes handling
        checkpoint_dict = {
            "thread_id": cp.thread_id,
            "checkpoint_ns": cp.checkpoint_ns,
            "checkpoint_id": cp.checkpoint_id,
            "parent_checkpoint_id": cp.parent_checkpoint_id,
            "type": cp.type,
            "checkpoint": cp.checkpoint,
            "metadata": _convert_metadata_to_dict(cp.metadata) if cp.metadata else {},
            "checkpoint_ns_hash": _bytes_to_hex(cp.checkpoint_ns_hash),
        }
        # Validate and create schema
        checkpoint_chain.append(CheckpointSchema(**checkpoint_dict))

    return TraceDetailResponse(
        trace=trace_graph,
        summary=summary,
        checkpoints=checkpoint_chain,
    )


@router.get("/threads/{thread_id}/analysis")
async def analyze_thread(
    thread_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze all checkpoints in a thread

    Args:
        thread_id: Thread identifier
        db: Database session

    Returns:
        Thread analysis with aggregated metrics
    """
    analyzer = CheckpointAnalyzer(db)
    analysis = analyzer.analyze_thread(thread_id)

    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])

    return analysis


@router.get("/threads/{thread_id}/timeline")
async def get_timeline(
    thread_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get checkpoint timeline for a thread

    Args:
        thread_id: Thread identifier
        limit: Maximum number of checkpoints
        db: Database session

    Returns:
        Timeline of checkpoints
    """
    analyzer = CheckpointAnalyzer(db)
    timeline = analyzer.get_checkpoint_timeline(thread_id, limit)

    return {
        "thread_id": thread_id,
        "timeline": timeline,
        "count": len(timeline),
    }


@router.get("/threads/{thread_id}/compare")
async def compare_checkpoints(
    thread_id: str,
    checkpoint_id_1: str = Query(..., description="First checkpoint ID"),
    checkpoint_id_2: str = Query(..., description="Second checkpoint ID"),
    db: Session = Depends(get_db)
):
    """
    Compare two checkpoints

    Args:
        thread_id: Thread identifier
        checkpoint_id_1: First checkpoint ID
        checkpoint_id_2: Second checkpoint ID
        db: Database session

    Returns:
        Comparison results
    """
    analyzer = CheckpointAnalyzer(db)

    try:
        comparison = analyzer.compare_checkpoints(
            thread_id, checkpoint_id_1, checkpoint_id_2
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/database/info")
async def get_database_info(db: Session = Depends(get_db)):
    """
    Get database information and statistics

    Returns:
        Database type, version, and statistics
    """
    adapter = get_adapter(db)
    return adapter.get_database_info()
