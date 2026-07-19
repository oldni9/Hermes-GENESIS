"""
===============================================================================
Hermes Integration Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class IntegrationError(Exception):
    """
    Base integration exception.
    """


class PipelineError(IntegrationError):
    """
    Integration pipeline failed.
    """


class PipelineValidationError(IntegrationError):
    """
    Invalid integration pipeline.
    """
