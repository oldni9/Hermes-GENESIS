"""
===============================================================================
Hermes Knowledge Search

High-level search engine built on top of KnowledgeIndex.

Responsibilities

    Query parsing

    Candidate retrieval

    Ranking

    Sorting

    Result generation

Future

    Semantic Search

    OCR Search

    Image Search

    Embedding Search

    Hybrid Retrieval

Author
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hermes.knowledge.document import KnowledgeDocument
from hermes.knowledge.index import KnowledgeIndex
from hermes.knowledge.tokenizer import KnowledgeTokenizer  # NEW IMPORT


# =============================================================================
# Search Result
# =============================================================================


@dataclass(slots=True)
class KnowledgeSearchResult:
    """
    Represents one ranked search result.
    """

    document: KnowledgeDocument

    score: float = 0.0

    matched_provider: str = ""

    matched_terms: list[str] = field(
        default_factory=list,
    )

    reason: str = ""


# =============================================================================
# Search Engine
# =============================================================================


class KnowledgeSearch:
    """
    Hermes search engine.

    The search engine never scans every document.

    It always asks the index first.
    """

    def __init__(
        self,
        index: KnowledgeIndex,
    ):
        self.index = index
        self.tokenizer = KnowledgeTokenizer()  # NEW

    # -----------------------------------------------------------------

    def search(
        self,
        query: str,
        limit: int = 25,
    ) -> list[KnowledgeSearchResult]:
        terms = self.tokenizer.tokenize(query)  # REPLACED

        candidates: dict[str, KnowledgeSearchResult] = {}

        for provider in self.index.providers():
            for term in terms:
                documents = self.index.search(
                    term,
                    provider=provider.name,
                )

                for document in documents:
                    existing = candidates.get(document.id)

                    if existing is None:
                        existing = KnowledgeSearchResult(
                            document=document,
                        )
                        candidates[document.id] = existing

                    existing.score += self._provider_weight(
                        provider.name,
                    )
                    existing.matched_provider = provider.name

                    if term not in existing.matched_terms:
                        existing.matched_terms.append(term)

                    existing.reason = (
                        f"Matched {provider.name}"
                    )

        results = list(
            candidates.values()
        )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]

    # -----------------------------------------------------------------

    def titles(
        self,
        query: str,
        limit: int = 25,
    ):
        return [
            result.document.title
            for result in self.search(
                query,
                limit,
            )
        ]

    # -----------------------------------------------------------------

    # REMOVED entire _tokenize method

    # -----------------------------------------------------------------

    @staticmethod
    def _provider_weight(
        provider: str,
    ) -> float:
        weights = {
            "title": 10.0,
            "tags": 8.0,
            "keywords": 5.0,
            "type": 3.0,
            "source": 2.0,
        }
        return weights.get(
            provider,
            1.0,
        )

    # -----------------------------------------------------------------

    def provider_search(
        self,
        provider: str,
        query: str,
        limit: int = 25,
    ) -> list[KnowledgeSearchResult]:
        terms = self.tokenizer.tokenize(query)  # REPLACED

        candidates: dict[str, KnowledgeSearchResult] = {}

        for term in terms:
            documents = self.index.search(
                term,
                provider=provider,
            )

            for document in documents:
                result = candidates.get(document.id)

                if result is None:
                    result = KnowledgeSearchResult(
                        document=document,
                    )
                    candidates[document.id] = result

                result.score += self._provider_weight(
                    provider,
                )
                result.matched_provider = provider

                if term not in result.matched_terms:
                    result.matched_terms.append(term)

                result.reason = (
                    f"Matched {provider}"
                )

        results = list(
            candidates.values()
        )

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[:limit]

    # -----------------------------------------------------------------

    def filter(
        self,
        results: list[KnowledgeSearchResult],
        *,
        document_type: str | None = None,
        source: str | None = None,
    ) -> list[KnowledgeSearchResult]:
        filtered: list[KnowledgeSearchResult] = []

        for result in results:
            document = result.document

            if document_type:
                if document.type != document_type:
                    continue

            if source:
                if document.source != source:
                    continue

            filtered.append(result)

        return filtered

    # -----------------------------------------------------------------

    def best(
        self,
        query: str,
    ) -> KnowledgeSearchResult | None:
        results = self.search(
            query,
            limit=1,
        )

        if results:
            return results[0]

        return None

    # -----------------------------------------------------------------

    def exists(
        self,
        query: str,
    ) -> bool:
        return self.best(query) is not None

    # -----------------------------------------------------------------

    def count(
        self,
        query: str,
    ) -> int:
        return len(
            self.search(query),
        )

    # -----------------------------------------------------------------

    def statistics(self):
        return {
            "documents": self.index.count(),
            "providers": len(
                tuple(
                    self.index.providers(),
                )
            ),
        }

    # -----------------------------------------------------------------

    #
    # Future hooks
    #
    # These intentionally do nothing today.
    #

    def semantic_search(
        self,
        query: str,
    ):
        raise NotImplementedError(
            "Semantic search provider not registered.",
        )

    # -----------------------------------------------------------------

    def embedding_search(
        self,
        embedding,
    ):
        raise NotImplementedError(
            "Embedding provider not registered.",
        )

    # -----------------------------------------------------------------

    def image_search(
        self,
        image,
    ):
        raise NotImplementedError(
            "Image provider not registered.",
        )

    # -----------------------------------------------------------------

    def ocr_search(
        self,
        query: str,
    ):
        raise NotImplementedError(
            "OCR provider not registered.",
        )