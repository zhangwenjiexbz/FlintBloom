"""
FlintBloom Client - Lightweight callback handler for LangChain/LangGraph

This is a standalone client that can be installed in your projects without
requiring the full FlintBloom server dependencies.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
import requests
import json


class FlintBloomCallbackHandler(BaseCallbackHandler):
    """
    Lightweight callback handler for LangChain/LangGraph with FlintBloom

    Supports both static and dynamic thread_id:

    Example 1 - Static thread_id:
        callback = FlintBloomCallbackHandler(thread_id="my-thread")
        llm = ChatOpenAI(callbacks=[callback])

    Example 2 - Dynamic thread_id from config:
        callback = FlintBloomCallbackHandler(api_url="http://localhost:8000")
        # Thread ID will be extracted from LangGraph config automatically
        app.invoke(input, config={"configurable": {"thread_id": "dynamic-123"}, "callbacks": [callback]})

    Example 3 - Custom thread_id resolver:
        def get_thread_id(metadata):
            return metadata.get("user_id", "default")

        callback = FlintBloomCallbackHandler(thread_id_resolver=get_thread_id)
    """

    def __init__(
        self,
        thread_id: Optional[str] = None,
        api_url: str = "http://localhost:8000/api/v1/realtime",
        enable_streaming: bool = True,
        thread_id_resolver: Optional[callable] = None,
        auto_detect_thread_id: bool = True,
    ):
        """
        Initialize callback handler

        Args:
            thread_id: Static thread identifier (optional if using dynamic detection)
            api_url: FlintBloom API URL
            enable_streaming: Whether to stream events in real-time
            thread_id_resolver: Custom function to resolve thread_id from metadata
            auto_detect_thread_id: Automatically detect thread_id from LangGraph config
        """
        super().__init__()
        self._static_thread_id = thread_id
        self.api_url = api_url.rstrip('/')
        self.enable_streaming = enable_streaming
        self.thread_id_resolver = thread_id_resolver
        self.auto_detect_thread_id = auto_detect_thread_id
        self.run_map: Dict[str, Dict[str, Any]] = {}
        self._current_thread_id: Optional[str] = None

    def _resolve_thread_id(self, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """
        Resolve thread_id from multiple sources with priority:
        1. Custom resolver function
        2. LangGraph config (configurable.thread_id)
        3. Metadata
        4. Static thread_id
        5. Generate from run_id
        """
        # Priority 1: Custom resolver
        if self.thread_id_resolver and metadata:
            try:
                resolved = self.thread_id_resolver(metadata)
                if resolved:
                    return resolved
            except Exception:
                pass

        # Priority 2: LangGraph config (from kwargs)
        if self.auto_detect_thread_id:
            # Check for configurable in kwargs
            if 'configurable' in kwargs:
                configurable = kwargs['configurable']
                if isinstance(configurable, dict) and 'thread_id' in configurable:
                    return configurable['thread_id']

            # Check in metadata
            if metadata:
                if 'configurable' in metadata:
                    configurable = metadata['configurable']
                    if isinstance(configurable, dict) and 'thread_id' in configurable:
                        return configurable['thread_id']

                # Check direct thread_id in metadata
                if 'thread_id' in metadata:
                    return metadata['thread_id']

        # Priority 3: Static thread_id
        if self._static_thread_id:
            return self._static_thread_id

        # Priority 4: Use cached thread_id
        if self._current_thread_id:
            return self._current_thread_id

        # Priority 5: Generate from run_id
        run_id = kwargs.get('run_id')
        if run_id:
            generated = f"auto-{str(run_id)[:8]}"
            self._current_thread_id = generated
            return generated

        # Fallback
        return "default-thread"

    def _get_run_info(self, run_id: UUID) -> Dict[str, Any]:
        """Get or create run information"""
        run_id_str = str(run_id)
        if run_id_str not in self.run_map:
            self.run_map[run_id_str] = {
                "run_id": run_id_str,
                "start_time": datetime.now(),
                "events": [],
            }
        return self.run_map[run_id_str]

    def _send_event(self, event: Dict[str, Any]) -> None:
        """Send event to FlintBloom API"""
        if not self.enable_streaming:
            return

        try:
            # Store event locally
            thread_id = event.get("thread_id")
            if thread_id:
                requests.post(
                    f"{self.api_url}/events",
                    json=event,
                    timeout=1
                )
        except Exception:
            # Silently fail to not interrupt the main execution
            pass

    # ============= LLM Callbacks =============

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts running"""
        thread_id = self._resolve_thread_id(metadata, **kwargs)

        run_info = self._get_run_info(run_id)
        run_info["type"] = "llm"
        run_info["thread_id"] = thread_id
        run_info["parent_run_id"] = str(parent_run_id) if parent_run_id else None
        run_info["prompts"] = prompts
        run_info["tags"] = tags or []
        run_info["metadata"] = metadata or {}

        event = {
            "event_type": "llm_start",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "prompts": prompts,
                "serialized": serialized,
                "tags": tags,
                "metadata": metadata,
            },
        }

        self._send_event(event)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM ends running"""
        run_info = self._get_run_info(run_id)
        thread_id = run_info.get("thread_id", self._resolve_thread_id(None, **kwargs))
        run_info["end_time"] = datetime.now()
        run_info["response"] = response

        duration_ms = (
            run_info["end_time"] - run_info["start_time"]
        ).total_seconds() * 1000

        token_usage = {}
        if response.llm_output and "token_usage" in response.llm_output:
            token_usage = response.llm_output["token_usage"]

        event = {
            "event_type": "llm_end",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "data": {
                "generations": [
                    [gen.text for gen in generation]
                    for generation in response.generations
                ],
                "llm_output": response.llm_output,
                "token_usage": token_usage,
            },
        }

        self._send_event(event)

    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM errors"""
        run_info = self._get_run_info(run_id)
        thread_id = run_info.get("thread_id", self._resolve_thread_id(None, **kwargs))
        run_info["end_time"] = datetime.now()
        run_info["error"] = str(error)

        event = {
            "event_type": "llm_error",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        }

        self._send_event(event)

    # ============= Chain Callbacks =============

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain starts running"""
        thread_id = self._resolve_thread_id(metadata, **kwargs)

        run_info = self._get_run_info(run_id)
        run_info["type"] = "chain"
        run_info["thread_id"] = thread_id
        run_info["parent_run_id"] = str(parent_run_id) if parent_run_id else None
        run_info["inputs"] = inputs
        run_info["tags"] = tags or []
        run_info["metadata"] = metadata or {}

        event = {
            "event_type": "chain_start",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "inputs": inputs,
                "serialized": serialized,
                "tags": tags,
                "metadata": metadata,
            },
        }

        self._send_event(event)

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain ends running"""
        run_info = self._get_run_info(run_id)
        thread_id = run_info.get("thread_id", self._resolve_thread_id(None, **kwargs))
        run_info["end_time"] = datetime.now()
        run_info["outputs"] = outputs

        duration_ms = (
            run_info["end_time"] - run_info["start_time"]
        ).total_seconds() * 1000

        event = {
            "event_type": "chain_end",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "data": {
                "outputs": outputs,
            },
        }

        self._send_event(event)

    def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain errors"""
        run_info = self._get_run_info(run_id)
        thread_id = run_info.get("thread_id", self._resolve_thread_id(None, **kwargs))
        run_info["end_time"] = datetime.now()
        run_info["error"] = str(error)

        event = {
            "event_type": "chain_error",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        }

        self._send_event(event)

    # ============= Tool Callbacks =============

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool starts running"""
        thread_id = self._resolve_thread_id(metadata, **kwargs)

        run_info = self._get_run_info(run_id)
        run_info["type"] = "tool"
        run_info["thread_id"] = thread_id
        run_info["parent_run_id"] = str(parent_run_id) if parent_run_id else None
        run_info["input"] = input_str
        run_info["tags"] = tags or []
        run_info["metadata"] = metadata or {}

        event = {
            "event_type": "tool_start",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "input": input_str,
                "serialized": serialized,
                "tags": tags,
                "metadata": metadata,
            },
        }

        self._send_event(event)

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool ends running"""
        run_info = self._get_run_info(run_id)
        thread_id = run_info.get("thread_id", self._resolve_thread_id(None, **kwargs))
        run_info["end_time"] = datetime.now()
        run_info["output"] = output

        duration_ms = (
            run_info["end_time"] - run_info["start_time"]
        ).total_seconds() * 1000

        event = {
            "event_type": "tool_end",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "data": {
                "output": output,
            },
        }

        self._send_event(event)

    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool errors"""
        run_info = self._get_run_info(run_id)
        thread_id = run_info.get("thread_id", self._resolve_thread_id(None, **kwargs))
        run_info["end_time"] = datetime.now()
        run_info["error"] = str(error)

        event = {
            "event_type": "tool_error",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        }

        self._send_event(event)

    def get_run_summary(self) -> Dict[str, Any]:
        """Get summary of all runs captured"""
        return {
            "total_runs": len(self.run_map),
            "runs": list(self.run_map.values()),
        }
