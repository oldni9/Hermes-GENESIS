"""
===============================================================================
Hermes AI Request

Generic request object used by every AI capability.

Examples

    OCR

    Vision

    Image Captioning

    Embeddings

    Speech Recognition

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AIRequest:
    """
    Generic AI request.
    """

    input: Any = None

    prompt: str = ""

    provider: str = ""

    model: str = ""

    task: str = ""

    options: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------

    def set(

        self,

        key: str,

        value: Any,

    ) -> None:

        self.options[key] = value

    # ------------------------------------------------------------------

    def get(

        self,

        key: str,

        default: Any = None,

    ) -> Any:

        return self.options.get(

            key,

            default,

        )

    # ------------------------------------------------------------------

    def remove(

        self,

        key: str,

    ) -> None:

        self.options.pop(

            key,

            None,

        )

    # ------------------------------------------------------------------

    def clear(self) -> None:

        self.options.clear()

        self.metadata.clear()

    # ------------------------------------------------------------------

    @property
    def is_file(self) -> bool:

        return isinstance(

            self.input,

            (str, Path),

        )

    # ------------------------------------------------------------------

    @property
    def is_text(self) -> bool:

        return isinstance(

            self.input,

            str,

        )

    # ------------------------------------------------------------------

    @property
    def is_empty(self) -> bool:

        return self.input is None