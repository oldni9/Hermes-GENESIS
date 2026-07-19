"""
===============================================================================
Hermes Knowledge Normalizer

Normalizes searchable text.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import re


class KnowledgeNormalizer:

    @staticmethod
    def normalize(text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        text = re.sub(r"[_\-]+", " ", text)

        text = re.sub(r"[^\w\s]", " ", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()
