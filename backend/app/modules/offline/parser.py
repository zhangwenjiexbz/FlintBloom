import pickle
import json
import msgpack
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from app.db.models import Checkpoint, CheckpointBlob, CheckpointWrite
from app.db.schemas import TraceNode, TraceEdge, TraceGraph, TokenUsage, CostMetrics, PerformanceMetrics, ExecutionSummary


class CheckpointParser:
    """
    Parser for LangGraph checkpoint data
    Handles deserialization of blob data and extraction of execution traces
    """

    def __init__(self):
        self.deserializers = {
            "msgpack": self._deserialize_msgpack,
            "pickle": self._deserialize_pickle,
            "json": self._deserialize_json,
        }

    def _deserialize_msgpack(self, data: bytes) -> Any:
        """Deserialize msgpack data"""
        try:
            return msgpack.unpackb(data, raw=False)
        except Exception as e:
            raise ValueError(f"Failed to deserialize msgpack: {e}")

    def _deserialize_pickle(self, data: bytes) -> Any:
        """Deserialize pickle data"""
        try:
            return pickle.loads(data)
        except Exception as e:
            raise ValueError(f"Failed to deserialize pickle: {e}")

    def _deserialize_json(self, data: bytes) -> Any:
        """Deserialize JSON data"""
        try:
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Failed to deserialize JSON: {e}")

    def deserialize_blob(self, blob: bytes, blob_type: str) -> Any:
        """
        Deserialize blob data based on type

        Args:
            blob: Binary data
            blob_type: Type of serialization (msgpack, pickle, json)

        Returns:
            Deserialized data
        """
        if not blob:
            return None

        deserializer = self.deserializers.get(blob_type.lower())
        if not deserializer:
            raise ValueError(f"Unsupported blob type: {blob_type}")

        return deserializer(blob)

    def parse_checkpoint(self, checkpoint: Checkpoint) -> Dict[str, Any]:
        """
        Parse checkpoint JSON data

        Args:
            checkpoint: Checkpoint model instance

        Returns:
            Parsed checkpoint data with metadata
        """
        checkpoint_data = checkpoint.checkpoint

        return {
            "thread_id": checkpoint.thread_id,
            "checkpoint_id": checkpoint.checkpoint_id,
            "parent_checkpoint_id": checkpoint.parent_checkpoint_id,
            "checkpoint_ns": checkpoint.checkpoint_ns,
            "type": checkpoint.type,
            "data": checkpoint_data,
            "metadata": checkpoint.metadata,
            "channel_values": checkpoint_data.get("channel_values", {}),
            "channel_versions": checkpoint_data.get("channel_versions", {}),
            "versions_seen": checkpoint_data.get("versions_seen", {}),
        }

    def parse_checkpoint_writes(
        self,
        writes: List[CheckpointWrite]
    ) -> List[Dict[str, Any]]:
        """
        Parse checkpoint write operations

        Args:
            writes: List of CheckpointWrite instances

        Returns:
            List of parsed write operations
        """
        parsed_writes = []

        for write in writes:
            try:
                deserialized_data = self.deserialize_blob(write.blob, write.type or "msgpack")

                parsed_writes.append({
                    "task_id": write.task_id,
                    "task_path": write.task_path,
                    "channel": write.channel,
                    "idx": write.idx,
                    "type": write.type,
                    "data": deserialized_data,
                })
            except Exception as e:
                parsed_writes.append({
                    "task_id": write.task_id,
                    "channel": write.channel,
                    "idx": write.idx,
                    "error": str(e),
                })

        return parsed_writes

    def parse_checkpoint_blobs(
        self,
        blobs: List[CheckpointBlob]
    ) -> Dict[str, Any]:
        """
        Parse checkpoint blob data

        Args:
            blobs: List of CheckpointBlob instances

        Returns:
            Dictionary mapping channels to their deserialized data
        """
        parsed_blobs = {}

        for blob in blobs:
            try:
                deserialized_data = self.deserialize_blob(blob.blob, blob.type)

                channel_key = f"{blob.channel}:{blob.version}"
                parsed_blobs[channel_key] = {
                    "channel": blob.channel,
                    "version": blob.version,
                    "type": blob.type,
                    "data": deserialized_data,
                }
            except Exception as e:
                channel_key = f"{blob.channel}:{blob.version}"
                parsed_blobs[channel_key] = {
                    "channel": blob.channel,
                    "version": blob.version,
                    "error": str(e),
                }

        return parsed_blobs

    def extract_trace_nodes(
        self,
        checkpoint: Checkpoint,
        writes: List[CheckpointWrite],
        blobs: Optional[List[CheckpointBlob]] = None
    ) -> List[TraceNode]:
        """
        Extract execution trace nodes from checkpoint data

        Args:
            checkpoint: Checkpoint instance
            writes: List of write operations
            blobs: Optional list of blob data

        Returns:
            List of trace nodes
        """
        nodes = []
        checkpoint_data = self.parse_checkpoint(checkpoint)
        parsed_writes = self.parse_checkpoint_writes(writes)

        # Parse blobs if available
        parsed_blobs = {}
        if blobs:
            parsed_blobs = self.parse_checkpoint_blobs(blobs)

        # Extract nodes from checkpoint channel values
        channel_values = checkpoint_data.get("channel_values", {})

        # Parse messages if available
        if "messages" in channel_values:
            messages = channel_values["messages"]
            for idx, msg in enumerate(messages):
                node = self._create_node_from_message(msg, idx, checkpoint.checkpoint_id)
                if node:
                    nodes.append(node)

        # Parse writes as execution steps
        for write in parsed_writes:
            node = self._create_node_from_write(write, checkpoint.checkpoint_id)
            if node:
                nodes.append(node)

        # Parse blobs as additional data nodes
        if parsed_blobs:
            blob_nodes = self._create_nodes_from_blobs(parsed_blobs, checkpoint.checkpoint_id)
            nodes.extend(blob_nodes)

        return nodes

    def _create_node_from_message(
        self,
        message: Any,
        idx: int,
        checkpoint_id: str
    ) -> Optional[TraceNode]:
        """Create trace node from message data"""
        if isinstance(message, dict):
            return TraceNode(
                id=f"{checkpoint_id}_msg_{idx}",
                type="message",
                name=message.get("type", "unknown"),
                status="success",
                input_data=message.get("content"),
                metadata=message,
            )
        return None

    def _create_node_from_write(
        self,
        write: Dict[str, Any],
        checkpoint_id: str
    ) -> Optional[TraceNode]:
        """Create trace node from write operation"""
        return TraceNode(
            id=f"{checkpoint_id}_{write['task_id']}_{write['idx']}",
            type="task",
            name=write.get("channel", "unknown"),
            status="success" if "error" not in write else "error",
            input_data=write.get("data"),
            error=write.get("error"),
            metadata={
                "task_id": write["task_id"],
                "task_path": write.get("task_path", ""),
                "channel": write["channel"],
            },
        )

    def _create_nodes_from_blobs(
        self,
        blobs: Dict[str, Any],
        checkpoint_id: str
    ) -> List[TraceNode]:
        """
        Create trace nodes from blob data

        Args:
            blobs: Parsed blob data dictionary
            checkpoint_id: Checkpoint identifier

        Returns:
            List of trace nodes from blobs
        """
        nodes = []

        for channel_key, blob_info in blobs.items():
            if "error" in blob_info:
                # Create error node for failed blob parsing
                nodes.append(TraceNode(
                    id=f"{checkpoint_id}_blob_error_{channel_key}",
                    type="blob",
                    name=f"blob_{blob_info.get('channel', 'unknown')}",
                    status="error",
                    error=blob_info["error"],
                    metadata={
                        "channel": blob_info.get("channel"),
                        "version": blob_info.get("version"),
                        "type": blob_info.get("type"),
                    },
                ))
            else:
                # Create node for successfully parsed blob
                data = blob_info.get("data")
                data_size = len(str(data)) if data is not None else 0

                # Create a more descriptive node based on blob type
                node_type = "blob"
                node_name = blob_info.get("channel", "unknown")

                # Enhance node info based on channel
                channel = blob_info.get("channel", "")
                if channel == "messages":
                    node_type = "messages_snapshot"
                    node_name = "messages"
                elif channel in ["__start", "__end"]:
                    node_type = "checkpoint_marker"
                    node_name = channel

                nodes.append(TraceNode(
                    id=f"{checkpoint_id}_blob_{channel_key}",
                    type=node_type,
                    name=node_name,
                    status="success",
                    input_data={
                        "channel": blob_info.get("channel"),
                        "version": blob_info.get("version"),
                        "blob_type": blob_info.get("type"),
                        "data_size_bytes": data_size,
                        "preview": self._create_data_preview(data, max_length=200),
                    } if data is not None else None,
                    metadata={
                        "channel": blob_info.get("channel"),
                        "version": blob_info.get("version"),
                        "type": blob_info.get("type"),
                        "has_data": data is not None,
                    },
                ))

        return nodes

    def _create_data_preview(self, data: Any, max_length: int = 200) -> str:
        """
        Create a preview string for data

        Args:
            data: Data to preview
            max_length: Maximum preview length

        Returns:
            Preview string
        """
        if data is None:
            return None

        data_str = str(data)
        if len(data_str) <= max_length:
            return data_str

        return data_str[:max_length] + "..."

    def build_trace_graph(
        self,
        checkpoint: Checkpoint,
        writes: List[CheckpointWrite],
        blobs: Optional[List[CheckpointBlob]] = None
    ) -> TraceGraph:
        """
        Build complete trace graph from checkpoint data

        Args:
            checkpoint: Checkpoint instance
            writes: List of write operations
            blobs: Optional list of blob data

        Returns:
            Complete trace graph
        """
        nodes = self.extract_trace_nodes(checkpoint, writes, blobs)
        edges = self._build_edges(nodes, checkpoint)

        # Convert metadata to dict if it's a MetaData object
        metadata = checkpoint.metadata
        if hasattr(metadata, '__dict__'):
            # It's a MetaData or similar object
            metadata = {
                "source": getattr(metadata, 'source', None),
                "writes": getattr(metadata, 'writes', []),
                "parents": getattr(metadata, 'parents', {}),
                "step": getattr(metadata, 'step', None),
            }
        elif not isinstance(metadata, dict):
            metadata = {}

        return TraceGraph(
            thread_id=checkpoint.thread_id,
            checkpoint_id=checkpoint.checkpoint_id,
            nodes=nodes,
            edges=edges,
            metadata=metadata,
        )

    def _build_edges(
        self,
        nodes: List[TraceNode],
        checkpoint: Checkpoint
    ) -> List[TraceEdge]:
        """Build edges between trace nodes"""
        edges = []

        # Build sequential edges
        for i in range(len(nodes) - 1):
            edges.append(TraceEdge(
                source=nodes[i].id,
                target=nodes[i + 1].id,
                label="next"
            ))

        return edges
