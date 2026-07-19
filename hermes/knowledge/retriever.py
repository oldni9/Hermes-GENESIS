"""
===============================================================================
Hermes Knowledge Retriever

Retrieves knowledge documents from the knowledge base.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Mapping, List, Optional  # <-- Added 'Any' here

from hermes.knowledge.document import KnowledgeDocument
from hermes.knowledge.index import KnowledgeIndex
from hermes.knowledge.search import KnowledgeSearch


class KnowledgeRetriever:
    """
    High-level retriever for knowledge documents.
    """

    def __init__(self, index: KnowledgeIndex):
        self.index = index
        self.search_engine = KnowledgeSearch(index)

    def retrieve(self, query: str, limit: int = 10) -> list[KnowledgeDocument]:
        """
        Retrieve documents matching a query.
        """
        results = self.search_engine.search(query, limit=limit)
        return [result.document for result in results]

    def retrieve_with_scores(self, query: str, limit: int = 10) -> list[tuple[KnowledgeDocument, float]]:
        """
        Retrieve documents with relevance scores.
        """
        results = self.search_engine.search(query, limit=limit)
        return [(result.document, result.score) for result in results]

    def retrieve_by_id(self, doc_id: str) -> KnowledgeDocument | None:
        """
        Retrieve a single document by ID.
        """
        return self.index.document(doc_id)

    # ... (rest of the file remains unchanged)