from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import asyncio
import json
from queue import Queue
import threading


class RealtimeCollector:
    """
    Real-time data collector for LangChain/LangGraph events
    Collects events from callbacks and makes them available for streaming
    """

    def __init__(self, buffer_size: int = 1000):
        """
        Initialize collector

        Args:
            buffer_size: Maximum number of events to buffer per thread
        """
        self.buffer_size = buffer_size
        self.events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.event_queues: Dict[str, Queue] = defaultdict(Queue)
        self.subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self.lock = threading.Lock()

    def collect_event(self, event: Dict[str, Any]) -> None:
        """
        Collect an event from callback handler

        Args:
            event: Event data dictionary
        """
        thread_id = event.get("thread_id")
        if not thread_id:
            return

        with self.lock:
            # Add to buffer
            self.events[thread_id].append(event)

            # Maintain buffer size
            if len(self.events[thread_id]) > self.buffer_size:
                self.events[thread_id] = self.events[thread_id][-self.buffer_size:]

            # Add to queue for real-time streaming
            self.event_queues[thread_id].put(event)

            # Notify WebSocket subscribers
            self._notify_subscribers(thread_id, event)

    def _notify_subscribers(self, thread_id: str, event: Dict[str, Any]) -> None:
        """Notify all WebSocket subscribers of new event"""
        if thread_id in self.subscribers:
            for queue in self.subscribers[thread_id]:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    # Skip if queue is full
                    pass

    def subscribe(self, thread_id: str) -> asyncio.Queue:
        """
        Subscribe to events for a specific thread

        Args:
            thread_id: Thread identifier

        Returns:
            Async queue that will receive events
        """
        queue = asyncio.Queue(maxsize=100)
        with self.lock:
            self.subscribers[thread_id].append(queue)
        return queue

    def unsubscribe(self, thread_id: str, queue: asyncio.Queue) -> None:
        """
        Unsubscribe from events

        Args:
            thread_id: Thread identifier
            queue: Queue to remove
        """
        with self.lock:
            if thread_id in self.subscribers:
                try:
                    self.subscribers[thread_id].remove(queue)
                except ValueError:
                    pass

    def get_events(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get buffered events for a thread

        Args:
            thread_id: Thread identifier
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of events
        """
        with self.lock:
            events = self.events.get(thread_id, [])
            if limit:
                return events[offset:offset + limit]
            return events[offset:]

    def get_event_count(self, thread_id: str) -> int:
        """Get total number of events for a thread"""
        with self.lock:
            return len(self.events.get(thread_id, []))

    def clear_events(self, thread_id: str) -> None:
        """Clear all events for a thread"""
        with self.lock:
            if thread_id in self.events:
                self.events[thread_id].clear()
            if thread_id in self.event_queues:
                while not self.event_queues[thread_id].empty():
                    try:
                        self.event_queues[thread_id].get_nowait()
                    except:
                        break

    def get_active_threads(self) -> List[str]:
        """Get list of threads with buffered events"""
        with self.lock:
            return list(self.events.keys())

    def get_summary(self, thread_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a thread

        Args:
            thread_id: Thread identifier

        Returns:
            Summary statistics
        """
        with self.lock:
            events = self.events.get(thread_id, [])

            if not events:
                return {
                    "thread_id": thread_id,
                    "event_count": 0,
                    "event_types": {},
                }

            # Count event types
            event_types = defaultdict(int)
            for event in events:
                event_type = event.get("event_type", "unknown")
                event_types[event_type] += 1

            # Calculate duration
            start_time = None
            end_time = None
            for event in events:
                timestamp = event.get("timestamp")
                if timestamp:
                    dt = datetime.fromisoformat(timestamp)
                    if start_time is None or dt < start_time:
                        start_time = dt
                    if end_time is None or dt > end_time:
                        end_time = dt

            duration_ms = None
            if start_time and end_time:
                duration_ms = (end_time - start_time).total_seconds() * 1000

            # Calculate token usage
            total_tokens = 0
            for event in events:
                if event.get("event_type") == "llm_end":
                    token_usage = event.get("data", {}).get("token_usage", {})
                    total_tokens += token_usage.get("total_tokens", 0)

            return {
                "thread_id": thread_id,
                "event_count": len(events),
                "event_types": dict(event_types),
                "duration_ms": duration_ms,
                "total_tokens": total_tokens,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
            }

    def export_events(self, thread_id: str, format: str = "json") -> str:
        """
        Export events in specified format

        Args:
            thread_id: Thread identifier
            format: Export format (json, jsonl)

        Returns:
            Formatted string
        """
        events = self.get_events(thread_id)

        if format == "json":
            return json.dumps(events, indent=2)
        elif format == "jsonl":
            return "\n".join(json.dumps(event) for event in events)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global collector instance
_global_collector: Optional[RealtimeCollector] = None


def get_global_collector() -> RealtimeCollector:
    """Get or create global collector instance"""
    global _global_collector
    if _global_collector is None:
        _global_collector = RealtimeCollector()
    return _global_collector
