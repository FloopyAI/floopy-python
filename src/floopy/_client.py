"""``Floopy`` (sync) and ``AsyncFloopy`` (async) clients.

Both wrap the official ``openai`` SDK pointed at the Floopy gateway — so
``client.chat`` / ``client.embeddings`` / ``client.models`` are 1:1 drop-in
replacements — and add the typed Floopy-only resources on top. Mirrors
``src/client.ts``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ._http import AsyncHTTP, SyncHTTP
from ._openai_delegate import create_async_openai_delegate, create_openai_delegate
from .resources import (
    AsyncBatchesResource,
    AsyncConstraintsResource,
    AsyncDecisionsResource,
    AsyncEvaluationsResource,
    AsyncExperimentsResource,
    AsyncExportResource,
    AsyncFeedbackResource,
    AsyncFilesResource,
    AsyncRoutingResource,
    AsyncSessionsResource,
    BatchesResource,
    ConstraintsResource,
    DecisionsResource,
    EvaluationsResource,
    ExperimentsResource,
    ExportResource,
    FeedbackResource,
    FilesResource,
    RoutingResource,
    SessionsResource,
)
from .types.shared import FloopyOptions

if TYPE_CHECKING:
    from openai import AsyncOpenAI, OpenAI
    from openai.resources import (
        AsyncEmbeddings,
        AsyncModels,
        Embeddings,
        Models,
    )
    from openai.resources.chat import AsyncChat, Chat


class Floopy:
    """Synchronous Floopy gateway client.

    Use as a context manager (``with Floopy(api_key=...) as f:``) or call
    :meth:`close` to release the underlying HTTP connections.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
        options: FloopyOptions | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._http = SyncHTTP(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_options=options,
            http_client=http_client,
        )
        self._openai: OpenAI | None = None

        self.feedback = FeedbackResource(self._http)
        self.decisions = DecisionsResource(self._http)
        self.experiments = ExperimentsResource(self._http)
        self.constraints = ConstraintsResource(self._http)
        self.export = ExportResource(self._http)
        self.evaluations = EvaluationsResource(self._http)
        self.routing = RoutingResource(self._http)
        self.sessions = SessionsResource(self._http)
        self.files = FilesResource(self._http)
        self.batches = BatchesResource(self._http)

    @property
    def openai(self) -> OpenAI:
        """Lazily-instantiated ``openai`` client pre-pointed at the gateway."""
        if self._openai is None:
            self._openai = create_openai_delegate(self._http)
        return self._openai

    @property
    def chat(self) -> Chat:
        return self.openai.chat

    @property
    def embeddings(self) -> Embeddings:
        return self.openai.embeddings

    @property
    def models(self) -> Models:
        return self.openai.models

    def close(self) -> None:
        self._http.close()
        if self._openai is not None:
            self._openai.close()

    def __enter__(self) -> Floopy:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncFloopy:
    """Asynchronous Floopy gateway client.

    Use as an async context manager (``async with AsyncFloopy(...) as f:``)
    or ``await f.aclose()`` to release the underlying HTTP connections.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
        options: FloopyOptions | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._http = AsyncHTTP(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_options=options,
            http_client=http_client,
        )
        self._openai: AsyncOpenAI | None = None

        self.feedback = AsyncFeedbackResource(self._http)
        self.decisions = AsyncDecisionsResource(self._http)
        self.experiments = AsyncExperimentsResource(self._http)
        self.constraints = AsyncConstraintsResource(self._http)
        self.export = AsyncExportResource(self._http)
        self.evaluations = AsyncEvaluationsResource(self._http)
        self.routing = AsyncRoutingResource(self._http)
        self.sessions = AsyncSessionsResource(self._http)
        self.files = AsyncFilesResource(self._http)
        self.batches = AsyncBatchesResource(self._http)

    @property
    def openai(self) -> AsyncOpenAI:
        if self._openai is None:
            self._openai = create_async_openai_delegate(self._http)
        return self._openai

    @property
    def chat(self) -> AsyncChat:
        return self.openai.chat

    @property
    def embeddings(self) -> AsyncEmbeddings:
        return self.openai.embeddings

    @property
    def models(self) -> AsyncModels:
        return self.openai.models

    async def aclose(self) -> None:
        await self._http.aclose()
        if self._openai is not None:
            await self._openai.close()

    async def __aenter__(self) -> AsyncFloopy:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
