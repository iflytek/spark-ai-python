"""**Tracers** are classes for tracing runs.

**Class hierarchy:**

.. code-block::

    BaseCallbackHandler --> BaseTracer --> <name>Tracer  # Examples: LangChainTracer, RootListenersTracer
                                       --> <name>  # Examples: LogStreamCallbackHandler
"""  # noqa: E501

__all__ = [
    "BaseTracer",
    "EvaluatorCallbackHandler",
    "LangChainTracer",
    "ConsoleCallbackHandler",
    "RunLog",
    "RunLogPatch",
    "LogStreamCallbackHandler",
]

from sparkai.core.tracers.base import BaseTracer
from sparkai.core.tracers.evaluation import EvaluatorCallbackHandler
from sparkai.core.tracers.langchain import LangChainTracer
from sparkai.core.tracers.log_stream import (
    LogStreamCallbackHandler,
    RunLog,
    RunLogPatch,
)
from sparkai.core.tracers.stdout import ConsoleCallbackHandler
