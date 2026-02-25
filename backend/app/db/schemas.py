from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


# ============= Checkpoint Schemas =============

class CheckpointBlobSchema(BaseModel):
    """Schema for checkpoint blob data"""
    thread_id: str
    checkpoint_ns: str = ""
    channel: str
    version: str
    type: str
    blob: Optional[bytes] = None
    checkpoint_ns_hash: bytes

    class Config:
        from_attributes = True


class CheckpointWriteSchema(BaseModel):
    """Schema for checkpoint write operations"""
    thread_id: str
    checkpoint_ns: str = ""
    checkpoint_id: str
    task_id: str
    idx: int
    channel: str
    type: Optional[str] = None
    blob: bytes
    checkpoint_ns_hash: bytes
    task_path: str = ""

    class Config:
        from_attributes = True


class CheckpointSchema(BaseModel):
    """Schema for checkpoint metadata"""
    thread_id: str
    checkpoint_ns: str = ""
    checkpoint_id: str
    parent_checkpoint_id: Optional[str] = None
    type: Optional[str] = None
    checkpoint: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    checkpoint_ns_hash: bytes

    class Config:
        from_attributes = True


# ============= Trace Visualization Schemas =============

class TraceNode(BaseModel):
    """Single node in execution trace"""
    id: str
    type: str  # "llm", "tool", "agent", "chain"
    name: str
    status: str  # "running", "success", "error"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)


class TraceEdge(BaseModel):
    """Edge connecting trace nodes"""
    source: str
    target: str
    label: Optional[str] = None


class TraceGraph(BaseModel):
    """Complete execution trace graph"""
    thread_id: str
    checkpoint_id: str
    nodes: List[TraceNode]
    edges: List[TraceEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============= Metrics Schemas =============

class TokenUsage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class CostMetrics(BaseModel):
    """Cost calculation metrics"""
    total_cost: float = 0.0
    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    currency: str = "USD"


class PerformanceMetrics(BaseModel):
    """Performance statistics"""
    total_duration_ms: float
    llm_duration_ms: float = 0.0
    tool_duration_ms: float = 0.0
    avg_llm_latency_ms: Optional[float] = None
    avg_tool_latency_ms: Optional[float] = None


class ExecutionSummary(BaseModel):
    """Summary of execution metrics"""
    thread_id: str
    checkpoint_id: str
    total_nodes: int
    success_count: int
    error_count: int
    token_usage: TokenUsage
    cost_metrics: CostMetrics
    performance_metrics: PerformanceMetrics
    created_at: datetime


# ============= Query Schemas =============

class ThreadListQuery(BaseModel):
    """Query parameters for listing threads"""
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="created_at", pattern="^(created_at|thread_id)$")
    order: str = Field(default="desc", pattern="^(asc|desc)$")


class CheckpointListQuery(BaseModel):
    """Query parameters for listing checkpoints"""
    thread_id: str
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TraceDetailQuery(BaseModel):
    """Query parameters for trace details"""
    thread_id: str
    checkpoint_id: str
    include_blobs: bool = False


# ============= Response Schemas =============

class ThreadInfo(BaseModel):
    """Thread information"""
    thread_id: str
    checkpoint_count: int
    latest_checkpoint_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ThreadListResponse(BaseModel):
    """Response for thread list"""
    threads: List[ThreadInfo]
    total: int
    limit: int
    offset: int


class CheckpointListResponse(BaseModel):
    """Response for checkpoint list"""
    checkpoints: List[CheckpointSchema]
    total: int
    limit: int
    offset: int


class TraceDetailResponse(BaseModel):
    """Response for trace details"""
    trace: TraceGraph
    summary: ExecutionSummary
    checkpoints: List[CheckpointSchema]
