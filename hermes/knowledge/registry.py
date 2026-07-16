"""
===============================================================================
Hermes Knowledge Registry

Stores every KnowledgeDocument known to Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.knowledge.document import KnowledgeDocument


class KnowledgeRegistry:
    """
    Central registry for KnowledgeDocument objects.
    """

    def __init__(self):

        self._documents: dict[str, KnowledgeDocument] = {}

    # ------------------------------------------------------------------

    def add(

        self,

        document: KnowledgeDocument,

    ) -> None:

        self._documents[document.id] = document

    # ------------------------------------------------------------------

    def remove(

        self,

        document_id: str,

    ) -> None:

        self._documents.pop(

            document_id,

            None,

        )

    # ------------------------------------------------------------------

    def get(

        self,

        document_id: str,

    ) -> KnowledgeDocument | None:

        return self._documents.get(

            document_id,

        )

    # ------------------------------------------------------------------

    def exists(

        self,

        document_id: str,

    ) -> bool:

        return document_id in self._documents

    # ------------------------------------------------------------------

    def all(self):

        return list(

            self._documents.values()

        )

    # ------------------------------------------------------------------

    def titles(self):

        return sorted(

            document.title

            for document in self._documents.values()

        )

    # ------------------------------------------------------------------

    def clear(self):

        self._documents.clear()

    # ------------------------------------------------------------------

    def count(self):

        return len(

            self._documents,

        )

    # ------------------------------------------------------------------

    def __len__(self):

        return len(

            self._documents,

        )

    # ------------------------------------------------------------------

    def __iter__(self):

        return iter(

            self._documents.values()

        )