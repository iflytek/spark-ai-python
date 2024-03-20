"""Schemas for tracers."""
from __future__ import annotations

import datetime
import warnings
from typing import Any, Dict, List, Optional, Type
from uuid import UUID


from sparkai.core._api import deprecated
from sparkai.core.outputs import LLMResult
from sparkai.core.pydantic_v1 import BaseModel, Field, root_validator




@deprecated("0.1.0", removal="0.2.0")
class TracerSessionV1Base(BaseModel):
    """Base class for TracerSessionV1."""

    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    name: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


@deprecated("0.1.0", removal="0.2.0")
class TracerSessionV1Create(TracerSessionV1Base):
    """Create class for TracerSessionV1."""


@deprecated("0.1.0", removal="0.2.0")
class TracerSessionV1(TracerSessionV1Base):
    """TracerSessionV1 schema."""

    id: int


@deprecated("0.1.0", removal="0.2.0")
class TracerSessionBase(TracerSessionV1Base):
    """Base class for TracerSession."""

    tenant_id: UUID


@deprecated("0.1.0", removal="0.2.0")
class TracerSession(TracerSessionBase):
    """TracerSessionV1 schema for the V2 API."""

    id: UUID


@deprecated("0.1.0", alternative="Run", removal="0.2.0")
class BaseRun(BaseModel):
    """Base class for Run."""

    uuid: str
    parent_uuid: Optional[str] = None
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    end_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    extra: Optional[Dict[str, Any]] = None
    execution_order: int
    child_execution_order: int
    serialized: Dict[str, Any]
    session_id: int
    error: Optional[str] = None


@deprecated("0.1.0", alternative="Run", removal="0.2.0")
class LLMRun(BaseRun):
    """Class for LLMRun."""

    prompts: List[str]
    response: Optional[LLMResult] = None


@deprecated("0.1.0", alternative="Run", removal="0.2.0")
class ChainRun(BaseRun):
    """Class for ChainRun."""

    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    child_llm_runs: List[LLMRun] = Field(default_factory=list)
    child_chain_runs: List[ChainRun] = Field(default_factory=list)
    child_tool_runs: List[ToolRun] = Field(default_factory=list)


@deprecated("0.1.0", alternative="Run", removal="0.2.0")
class ToolRun(BaseRun):
    """Class for ToolRun."""

    tool_input: str
    output: Optional[str] = None
    action: str
    child_llm_runs: List[LLMRun] = Field(default_factory=list)
    child_chain_runs: List[ChainRun] = Field(default_factory=list)
    child_tool_runs: List[ToolRun] = Field(default_factory=list)


# Begin V2 API Schemas




__all__ = [
    "BaseRun",
    "ChainRun",
    "LLMRun",
    "ToolRun",
    "TracerSession",
    "TracerSessionBase",
    "TracerSessionV1",
    "TracerSessionV1Base",
    "TracerSessionV1Create",
]
