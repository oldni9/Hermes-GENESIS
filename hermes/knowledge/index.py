"""
===============================================================================
Hermes Knowledge Index

High-performance multi-index engine for Hermes.

This module is responsible for indexing every KnowledgeDocument inside Hermes
without knowing anything about OCR, embeddings, image analysis or future AI
systems.

Future AI capabilities simply register additional index providers.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from collections import defaultdict

from dataclasses import dataclass

from hermes.knowledge.document import KnowledgeDocument
from hermes.knowledge.tokenizer import KnowledgeTokenizer  # NEW IMPORT

# =============================================================================
# Index Statistics
# =============================================================================


@dataclass(slots=True)
class IndexStatistics:

    documents: int = 0

    providers: int = 0

    entries: int = 0


# =============================================================================
# Tokenizer singleton
# =============================================================================

_tokenizer = KnowledgeTokenizer()  # NEW


# =============================================================================
# Base Provider
# =============================================================================


class BaseIndexProvider(ABC):
    """
    Every searchable field inside Hermes derives from this class.

    Examples:

        TitleIndexProvider
        TagIndexProvider
        OCRIndexProvider
        EmbeddingIndexProvider
        FaceIndexProvider
    """

    name = "base"

    def __init__(self):

        self._index: dict[str, set[str]] = defaultdict(set)

    # -----------------------------------------------------------------

    @abstractmethod
    def values(
        self,
        document: KnowledgeDocument,
    ) -> list[str]:
        """
        Return every searchable token belonging to the document.
        """

    # -----------------------------------------------------------------

    def add(
        self,
        document: KnowledgeDocument,
    ):

        for value in self.values(document):

            if value:

                self._index[value.lower()].add(document.id)

    # -----------------------------------------------------------------

    def remove(
        self,
        document: KnowledgeDocument,
    ):

        for value in self.values(document):

            key = value.lower()

            ids = self._index.get(key)

            if ids is None:

                continue

            ids.discard(document.id)

            if not ids:

                self._index.pop(key, None)

    # -----------------------------------------------------------------

    def search(
        self,
        value: str,
    ) -> set[str]:

        return set(
            self._index.get(
                value.lower(),
                set(),
            )
        )

    # -----------------------------------------------------------------

    def clear(self):

        self._index.clear()

    # -----------------------------------------------------------------

    def count(self):

        return sum(len(ids) for ids in self._index.values())


# =============================================================================
# Built-in Providers
# =============================================================================


class TitleIndexProvider(BaseIndexProvider):

    name = "title"

    def values(self, document):

        # REPLACED: use tokenizer instead of returning document.title directly
        return _tokenizer.tokenize(document.title or "")


class TagIndexProvider(BaseIndexProvider):

    name = "tags"

    def values(self, document):

        # REPLACED: tokenize every tag
        tokens = []
        for tag in document.tags:
            tokens.extend(_tokenizer.tokenize(tag))
        return tokens


class TypeIndexProvider(BaseIndexProvider):

    name = "type"

    def values(self, document):

        # REPLACED: tokenize document.type
        return _tokenizer.tokenize(document.type or "")


class SourceIndexProvider(BaseIndexProvider):

    name = "source"

    def values(self, document):

        # REPLACED: tokenize document.source
        return _tokenizer.tokenize(document.source or "")


class KeywordIndexProvider(BaseIndexProvider):
    """
    Temporary keyword provider.

    Later this will be replaced by

        OCR

        NLP

        Embeddings

        AI keyword extraction
    """

    name = "keywords"

    def values(self, document):

        # REPLACED: use tokenizer on combined text
        text = f"{document.title} {document.content}"
        return _tokenizer.tokenize(text)


# =============================================================================
# Knowledge Index
# =============================================================================


class KnowledgeIndex:
    """
    Central indexing engine.

    The manager owns documents.

    The index owns searchable structures.

    Search never iterates every document.
    """

    def __init__(self):

        self._documents: dict[str, KnowledgeDocument] = {}

        self._providers: dict[str, BaseIndexProvider] = {}

        self.register(TitleIndexProvider())

        self.register(TagIndexProvider())

        self.register(TypeIndexProvider())

        self.register(SourceIndexProvider())

        self.register(KeywordIndexProvider())

    # -----------------------------------------------------------------

    def register(
        self,
        provider: BaseIndexProvider,
    ):

        self._providers[provider.name] = provider

    # -----------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ):

        self._providers.pop(name, None)

    # -----------------------------------------------------------------

    def providers(self):

        return tuple(self._providers.values())

    # -----------------------------------------------------------------

    def provider(
        self,
        name: str,
    ):

        return self._providers.get(name)

    # -----------------------------------------------------------------

    def add(
        self,
        document: KnowledgeDocument,
    ):

        if document.id in self._documents:

            self.update(document)

            return

        self._documents[document.id] = document

        for provider in self._providers.values():

            provider.add(document)

    # -----------------------------------------------------------------

    def remove(
        self,
        document_id: str,
    ):

        document = self._documents.pop(
            document_id,
            None,
        )

        if document is None:

            return

        for provider in self._providers.values():

            provider.remove(document)

    # -----------------------------------------------------------------

    def update(
        self,
        document: KnowledgeDocument,
    ):

        old = self._documents.get(document.id)

        if old is not None:

            for provider in self._providers.values():

                provider.remove(old)

        self._documents[document.id] = document

        for provider in self._providers.values():

            provider.add(document)

    # -----------------------------------------------------------------

    def rebuild(self):

        documents = list(self._documents.values())

        for provider in self._providers.values():

            provider.clear()

        for document in documents:

            for provider in self._providers.values():

                provider.add(document)

    # -----------------------------------------------------------------

    def clear(self):

        self._documents.clear()

        for provider in self._providers.values():

            provider.clear()

    # -----------------------------------------------------------------

    def search(
        self,
        value: str,
        provider: str | None = None,
    ) -> list[KnowledgeDocument]:

        ids: set[str] = set()

        if provider:

            p = self.provider(provider)

            if p:

                ids |= p.search(value)

        else:

            for p in self.providers():

                ids |= p.search(value)

        return [self._documents[i] for i in ids if i in self._documents]

    # -----------------------------------------------------------------

    def document(
        self,
        document_id: str,
    ) -> KnowledgeDocument | None:

        return self._documents.get(document_id)

    # -----------------------------------------------------------------

    def documents(self):

        return tuple(self._documents.values())

    # -----------------------------------------------------------------

    def count(self):

        return len(
            self._documents,
        )

    # -----------------------------------------------------------------

    def statistics(
        self,
    ) -> IndexStatistics:

        stats = IndexStatistics()

        stats.documents = len(self._documents)

        stats.providers = len(self._providers)

        stats.entries = sum(provider.count() for provider in self.providers())

        return stats

    # -----------------------------------------------------------------

    def __contains__(
        self,
        document_id: str,
    ):

        return document_id in self._documents

    # -----------------------------------------------------------------

    def __len__(self):

        return len(self._documents)

    # -----------------------------------------------------------------

    def __iter__(self):

        return iter(self._documents.values())
