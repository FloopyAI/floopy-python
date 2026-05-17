"""Official Floopy AI Gateway SDK for Python.

Drop-in replacement for the ``openai`` SDK with Floopy's cache, audit,
experiments, routing, and security on top.

    from floopy import Floopy

    with Floopy(api_key="fl_...") as floopy:
        r = floopy.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello from Floopy!"}],
        )
"""

from __future__ import annotations

from ._client import AsyncFloopy, Floopy
from ._constants import (
    DEFAULT_BASE_URL,
    FLOOPY_CONFIRM_VALUES,
    FLOOPY_HEADERS,
)
from ._errors import (
    FloopyAuthError,
    FloopyConflictError,
    FloopyConnectionError,
    FloopyError,
    FloopyNotFoundError,
    FloopyPlanError,
    FloopyRateLimitError,
    FloopyServerError,
    FloopyTimeoutError,
    FloopyValidationError,
)
from ._version import __version__
from .resources import AsyncDecisionExportStream, DecisionExportStream
from .types import (
    CacheOptions,
    Decision,
    DecisionListPage,
    EvaluationResultRow,
    EvaluationResultsPage,
    EvaluationRun,
    EvaluationStatus,
    Experiment,
    ExperimentListPage,
    ExperimentResults,
    ExperimentStatus,
    ExportedDecisionRow,
    ExportFormat,
    ExportTrailer,
    FeedbackSubmitResponse,
    FirewallDecision,
    FloopyOptions,
    OrgConstraints,
    PaginatedResponse,
    RequestOptions,
    RoutingExplainResult,
    Session,
    SessionTurn,
    VariantResults,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "FLOOPY_CONFIRM_VALUES",
    "FLOOPY_HEADERS",
    "AsyncDecisionExportStream",
    "AsyncFloopy",
    "CacheOptions",
    "Decision",
    "DecisionExportStream",
    "DecisionListPage",
    "EvaluationResultRow",
    "EvaluationResultsPage",
    "EvaluationRun",
    "EvaluationStatus",
    "Experiment",
    "ExperimentListPage",
    "ExperimentResults",
    "ExperimentStatus",
    "ExportFormat",
    "ExportTrailer",
    "ExportedDecisionRow",
    "FeedbackSubmitResponse",
    "FirewallDecision",
    "Floopy",
    "FloopyAuthError",
    "FloopyConflictError",
    "FloopyConnectionError",
    "FloopyError",
    "FloopyNotFoundError",
    "FloopyOptions",
    "FloopyPlanError",
    "FloopyRateLimitError",
    "FloopyServerError",
    "FloopyTimeoutError",
    "FloopyValidationError",
    "OrgConstraints",
    "PaginatedResponse",
    "RequestOptions",
    "RoutingExplainResult",
    "Session",
    "SessionTurn",
    "VariantResults",
    "__version__",
]
