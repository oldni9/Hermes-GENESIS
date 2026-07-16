"""
===============================================================================
Hermes Knowledge Manager

Owns every KnowledgeDocument inside Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.knowledge.document import KnowledgeDocument
from hermes.knowledge.registry import KnowledgeRegistry


class KnowledgeManager:
    """
    Central manager for Hermes knowledge.
    """

    def __init__(self):

        self.registry = KnowledgeRegistry()

    # ------------------------------------------------------------------

    def add(

        self,

        document: KnowledgeDocument,

    ) -> None:

        self.registry.add(document)

    # ------------------------------------------------------------------

    def remove(

        self,

        document_id: str,

    ) -> None:

        self.registry.remove(document_id)

    # ------------------------------------------------------------------

    def get(

        self,

        document_id: str,

    ) -> KnowledgeDocument | None:

        return self.registry.get(document_id)

    # ------------------------------------------------------------------

    def exists(

        self,

        document_id: str,

    ) -> bool:

        return self.registry.exists(document_id)

    # ------------------------------------------------------------------

    def documents(self):

        return self.registry.all()

    # ------------------------------------------------------------------

    def titles(self):

        return self.registry.titles()

    # ------------------------------------------------------------------

    def count(self):

        return self.registry.count()

    # ------------------------------------------------------------------

    def clear(self):

        self.registry.clear()

    # ------------------------------------------------------------------

    def __len__(self):

        return len(self.registry)

    # ------------------------------------------------------------------

    def __iter__(self):

        return iter(self.registry)