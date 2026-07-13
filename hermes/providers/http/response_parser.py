"""
===============================================================================
Hermes Response Parser
===============================================================================
"""

from __future__ import annotations


class ResponseParser:

    @staticmethod
    def text(
        response: dict,
    ) -> str:

        if "choices" in response:

            return response["choices"][0]["message"]["content"]

        if "text" in response:

            return response["text"]

        return str(response)