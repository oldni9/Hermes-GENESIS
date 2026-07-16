"""
===============================================================================
Hermes AI Events

Central event definitions for AI execution.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class AIEvents:
    """
    Standard AI event names.
    """

    # ---------------------------------------------------------
    # Provider
    # ---------------------------------------------------------

    PROVIDER_REGISTERED = "ai.provider.registered"
    PROVIDER_UNREGISTERED = "ai.provider.unregistered"

    # ---------------------------------------------------------
    # Request
    # ---------------------------------------------------------

    REQUEST_CREATED = "ai.request.created"
    REQUEST_STARTED = "ai.request.started"
    REQUEST_COMPLETED = "ai.request.completed"
    REQUEST_FAILED = "ai.request.failed"

    # ---------------------------------------------------------
    # Pipeline
    # ---------------------------------------------------------

    PIPELINE_STARTED = "ai.pipeline.started"
    PIPELINE_FINISHED = "ai.pipeline.finished"

    # ---------------------------------------------------------
    # Cache
    # ---------------------------------------------------------

    CACHE_HIT = "ai.cache.hit"
    CACHE_MISS = "ai.cache.miss"

    # ---------------------------------------------------------
    # Models
    # ---------------------------------------------------------

    MODEL_LOADED = "ai.model.loaded"
    MODEL_UNLOADED = "ai.model.unloaded"

    # ---------------------------------------------------------
    # OCR
    # ---------------------------------------------------------

    OCR_STARTED = "ai.ocr.started"
    OCR_COMPLETED = "ai.ocr.completed"

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------

    VISION_STARTED = "ai.vision.started"
    VISION_COMPLETED = "ai.vision.completed"

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    EMBEDDING_STARTED = "ai.embedding.started"
    EMBEDDING_COMPLETED = "ai.embedding.completed"

    # ---------------------------------------------------------
    # Speech
    # ---------------------------------------------------------

    SPEECH_STARTED = "ai.speech.started"
    SPEECH_COMPLETED = "ai.speech.completed"

    @classmethod
    def all(cls) -> list[str]:

        return [

            value

            for key, value in vars(cls).items()

            if key.isupper()

        ]