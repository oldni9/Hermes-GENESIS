"""
===============================================================================
Hermes Request Builder

Converts a Prompt to an AIRequest.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Any

from hermes.ai.prompt import Prompt
from hermes.ai.request import AIRequest


class RequestBuilder:
    """
    Stateless utility to convert a Prompt to an AIRequest.
    """

    def build(
        self,
        prompt: Prompt,
        task: str = "chat",
        provider: str | None = None,
        model: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> AIRequest:
        """
        Convert a Prompt to an AIRequest.

        Parameters
        ----------
        prompt : Prompt
            The prompt to convert.
        task : str, default="chat"
            The task type.
        provider : str | None, optional
            Override provider.
        model : str | None, optional
            Override model.
        options : dict[str, Any] | None, optional
            Additional options.

        Returns
        -------
        AIRequest
            The constructed request.
        """
        request = prompt.to_request()
        request.task = task

        if provider:
            request.provider = provider
        if model:
            request.model = model
        if options:
            request.options.update(options)

        return request