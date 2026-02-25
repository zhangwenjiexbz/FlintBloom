"""
FlintBloom Client Package

Lightweight client for integrating FlintBloom observability into your
LangChain/LangGraph applications.
"""

__version__ = "0.1.0"

from flintbloom.callbacks import FlintBloomCallbackHandler

__all__ = ["FlintBloomCallbackHandler"]
