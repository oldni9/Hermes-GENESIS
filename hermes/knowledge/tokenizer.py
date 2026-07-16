"""
===============================================================================
Hermes Knowledge Tokenizer

Creates searchable tokens.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.knowledge.normalizer import KnowledgeNormalizer


class KnowledgeTokenizer:

    def tokenize(

        self,

        text: str,

    ) -> list[str]:

        normalized = KnowledgeNormalizer.normalize(text)

        if not normalized:

            return []

        tokens = []

        words = normalized.split()

        tokens.extend(words)

        if len(words) > 1:

            tokens.append(" ".join(words))

        return list(dict.fromkeys(tokens))