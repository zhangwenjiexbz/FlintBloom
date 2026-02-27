from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Checkpoint, CheckpointWrite, CheckpointBlob
from app.db.adapters import get_adapter
from app.db.schemas import (
    ExecutionSummary,
    TokenUsage,
    CostMetrics,
    PerformanceMetrics,
    TraceGraph,
)
from app.modules.offline.parser import CheckpointParser


class CheckpointAnalyzer:
    """
    Analyzer for checkpoint data
    Calculates metrics, statistics, and insights from checkpoint data
    """

    def __init__(self, session: Session):
        self.session = session
        self.adapter = get_adapter(session)
        self.parser = CheckpointParser()

    def analyze_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Analyze all checkpoints in a thread

        Args:
            thread_id: Thread identifier

        Returns:
            Thread analysis with statistics
        """
        checkpoints, total = self.adapter.get_checkpoints_by_thread(
            thread_id=thread_id,
            limit=1000,
            offset=0
        )

        if not checkpoints:
            return {
                "thread_id": thread_id,
                "checkpoint_count": 0,
                "error": "No checkpoints found"
            }

        # Analyze each checkpoint
        checkpoint_summaries = []
        for checkpoint in checkpoints:
            summary = self.analyze_checkpoint(
                thread_id=thread_id,
                checkpoint_id=checkpoint.checkpoint_id
            )
            checkpoint_summaries.append(summary)

        # Aggregate statistics
        total_tokens = sum(s.token_usage.total_tokens for s in checkpoint_summaries)
        total_cost = sum(s.cost_metrics.total_cost for s in checkpoint_summaries)
        total_duration = sum(s.performance_metrics.total_duration_ms for s in checkpoint_summaries)

        return {
            "thread_id": thread_id,
            "checkpoint_count": len(checkpoints),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "total_duration_ms": total_duration,
            "avg_tokens_per_checkpoint": total_tokens / len(checkpoints) if checkpoints else 0,
            "avg_cost_per_checkpoint": total_cost / len(checkpoints) if checkpoints else 0,
            "checkpoints": checkpoint_summaries,
        }

    def analyze_checkpoint(
        self,
        thread_id: str,
        checkpoint_id: str
    ) -> ExecutionSummary:
        """
        Analyze a single checkpoint

        Args:
            thread_id: Thread identifier
            checkpoint_id: Checkpoint identifier

        Returns:
            Execution summary with metrics
        """
        # Get checkpoint data
        checkpoint = self.adapter.get_checkpoint(thread_id, checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        # Get related data
        writes = self.adapter.get_checkpoint_writes(thread_id, checkpoint_id)
        blobs = self.adapter.get_checkpoint_blobs(thread_id)

        # Parse checkpoint
        parsed_checkpoint = self.parser.parse_checkpoint(checkpoint)
        trace_graph = self.parser.build_trace_graph(checkpoint, writes, blobs)

        # Calculate metrics
        token_usage = self._calculate_token_usage(parsed_checkpoint, trace_graph)
        cost_metrics = self._calculate_cost(token_usage)
        performance_metrics = self._calculate_performance(trace_graph)

        # Count successes and errors
        success_count = sum(1 for node in trace_graph.nodes if node.status == "success")
        error_count = sum(1 for node in trace_graph.nodes if node.status == "error")

        return ExecutionSummary(
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
            total_nodes=len(trace_graph.nodes),
            success_count=success_count,
            error_count=error_count,
            token_usage=token_usage,
            cost_metrics=cost_metrics,
            performance_metrics=performance_metrics,
            created_at=datetime.now(),
        )

    def _calculate_token_usage(
        self,
        parsed_checkpoint: Dict[str, Any],
        trace_graph: TraceGraph
    ) -> TokenUsage:
        """Calculate token usage from checkpoint data"""
        prompt_tokens = 0
        completion_tokens = 0

        # Extract token usage from metadata
        metadata = parsed_checkpoint.get("metadata", {})
        if "usage" in metadata:
            usage = metadata["usage"]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

        # Try to extract from channel values
        channel_values = parsed_checkpoint.get("channel_values", {})
        if "messages" in channel_values:
            for msg in channel_values["messages"]:
                if isinstance(msg, dict) and "usage_metadata" in msg:
                    usage = msg["usage_metadata"]
                    prompt_tokens += usage.get("input_tokens", 0)
                    completion_tokens += usage.get("output_tokens", 0)

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    def _calculate_cost(self, token_usage: TokenUsage) -> CostMetrics:
        """
        Calculate cost based on token usage
        Using approximate pricing (can be configured)
        """
        # Default pricing (USD per 1M tokens) - adjust based on model
        PROMPT_PRICE_PER_1M = 3.0  # $3 per 1M input tokens
        COMPLETION_PRICE_PER_1M = 15.0  # $15 per 1M output tokens

        prompt_cost = (token_usage.prompt_tokens / 1_000_000) * PROMPT_PRICE_PER_1M
        completion_cost = (token_usage.completion_tokens / 1_000_000) * COMPLETION_PRICE_PER_1M

        return CostMetrics(
            total_cost=prompt_cost + completion_cost,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            currency="USD",
        )

    def _calculate_performance(self, trace_graph: TraceGraph) -> PerformanceMetrics:
        """Calculate performance metrics from trace graph"""
        total_duration = 0.0
        llm_duration = 0.0
        tool_duration = 0.0
        llm_count = 0
        tool_count = 0

        for node in trace_graph.nodes:
            if node.duration_ms:
                total_duration += node.duration_ms

                if node.type == "llm":
                    llm_duration += node.duration_ms
                    llm_count += 1
                elif node.type == "tool":
                    tool_duration += node.duration_ms
                    tool_count += 1

        return PerformanceMetrics(
            total_duration_ms=total_duration,
            llm_duration_ms=llm_duration,
            tool_duration_ms=tool_duration,
            avg_llm_latency_ms=llm_duration / llm_count if llm_count > 0 else None,
            avg_tool_latency_ms=tool_duration / tool_count if tool_count > 0 else None,
        )

    def get_checkpoint_timeline(
        self,
        thread_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of checkpoints for a thread

        Args:
            thread_id: Thread identifier
            limit: Maximum number of checkpoints

        Returns:
            List of checkpoint timeline entries
        """
        checkpoints, _ = self.adapter.get_checkpoints_by_thread(
            thread_id=thread_id,
            limit=limit,
            offset=0
        )

        timeline = []
        for checkpoint in checkpoints:
            parsed = self.parser.parse_checkpoint(checkpoint)
            timeline.append({
                "checkpoint_id": checkpoint.checkpoint_id,
                "parent_checkpoint_id": checkpoint.parent_checkpoint_id,
                "metadata": checkpoint.metadata,
                "channel_count": len(parsed.get("channel_values", {})),
                "has_messages": "messages" in parsed.get("channel_values", {}),
            })

        return timeline

    def compare_checkpoints(
        self,
        thread_id: str,
        checkpoint_id_1: str,
        checkpoint_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two checkpoints

        Args:
            thread_id: Thread identifier
            checkpoint_id_1: First checkpoint ID
            checkpoint_id_2: Second checkpoint ID

        Returns:
            Comparison results
        """
        summary_1 = self.analyze_checkpoint(thread_id, checkpoint_id_1)
        summary_2 = self.analyze_checkpoint(thread_id, checkpoint_id_2)

        return {
            "checkpoint_1": {
                "checkpoint_id": checkpoint_id_1,
                "summary": summary_1,
            },
            "checkpoint_2": {
                "checkpoint_id": checkpoint_id_2,
                "summary": summary_2,
            },
            "differences": {
                "token_diff": summary_2.token_usage.total_tokens - summary_1.token_usage.total_tokens,
                "cost_diff": summary_2.cost_metrics.total_cost - summary_1.cost_metrics.total_cost,
                "duration_diff": summary_2.performance_metrics.total_duration_ms - summary_1.performance_metrics.total_duration_ms,
                "node_count_diff": summary_2.total_nodes - summary_1.total_nodes,
            }
        }
