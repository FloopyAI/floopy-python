"""Static configuration: defaults, Floopy wire headers, and API endpoints.

Mirrors ``src/constants/*`` in the Node SDK so behaviour stays in lockstep.
"""

from __future__ import annotations

# --- defaults -------------------------------------------------------------

DEFAULT_BASE_URL = "https://api.floopy.ai/v1"
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_USER_AGENT_PREFIX = "floopy-sdk"


# --- headers --------------------------------------------------------------


class FLOOPY_HEADERS:
    """Header names recognised by the gateway. Names are case-insensitive on
    the wire but kept verbatim to match the Node SDK and the gateway docs."""

    CACHE_ENABLED = "Floopy-Cache-Enabled"
    CACHE_BUCKET_MAX_SIZE = "Floopy-Cache-Bucket-Max-Size"
    PROMPT_ID = "Floopy-Prompt-Id"
    PROMPT_VERSION = "Floopy-Prompt-Version"
    LLM_SECURITY_ENABLED = "floopy-llm-security-enabled"
    CONFIRM = "X-Floopy-Confirm"
    REQUEST_ID = "X-Request-Id"
    AUTHORIZATION = "Authorization"
    CONTENT_TYPE = "Content-Type"
    USER_AGENT = "User-Agent"


class FLOOPY_CONFIRM_VALUES:
    EXPERIMENTS = "experiments"


# --- endpoints ------------------------------------------------------------

from urllib.parse import quote  # noqa: E402


def _seg(value: str) -> str:
    """Percent-encode a single path segment (matches JS ``encodeURIComponent``)."""
    return quote(value, safe="")


class ENDPOINTS:
    FEEDBACK = "/feedback"
    DECISIONS = "/decisions"
    EXPERIMENTS = "/experiments"
    CONSTRAINTS = "/constraints"
    EXPORT_DECISIONS = "/export/decisions"
    ROUTING_EXPLAIN = "/routing/explain"
    EVALUATIONS = "/evaluations"

    @staticmethod
    def decision_by_id(decision_id: str) -> str:
        return f"/decisions/{_seg(decision_id)}"

    @staticmethod
    def session_by_id(session_id: str) -> str:
        return f"/session/{_seg(session_id)}"

    @staticmethod
    def experiment_results(experiment_id: str) -> str:
        return f"/experiments/{_seg(experiment_id)}/results"

    @staticmethod
    def experiment_rollback(experiment_id: str) -> str:
        return f"/experiments/{_seg(experiment_id)}/rollback"

    @staticmethod
    def evaluation_by_id(evaluation_id: str) -> str:
        return f"/evaluations/{_seg(evaluation_id)}"

    @staticmethod
    def evaluation_results(evaluation_id: str) -> str:
        return f"/evaluations/{_seg(evaluation_id)}/results"

    @staticmethod
    def evaluation_cancel(evaluation_id: str) -> str:
        return f"/evaluations/{_seg(evaluation_id)}/cancel"
