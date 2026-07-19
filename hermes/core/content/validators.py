"""
===============================================================================
Content Validators – shared validation functions
===============================================================================
"""
from __future__ import annotations

import os
from typing import Optional, Union

def validate_mime_type(mime: Optional[str]) -> None:
    if mime is not None and not isinstance(mime, str):
        raise TypeError("mime_type must be a string or None")
    if mime is not None and "/" not in mime:
        raise ValueError(f"Invalid MIME type format: {mime!r}")

def validate_dimensions(width: Optional[int], height: Optional[int]) -> None:
    if width is not None and not isinstance(width, int):
        raise TypeError("width must be an int or None")
    if height is not None and not isinstance(height, int):
        raise TypeError("height must be an int or None")
    if width is not None and width < 0:
        raise ValueError("width must be non-negative")
    if height is not None and height < 0:
        raise ValueError("height must be non-negative")

def validate_duration(duration: Optional[float]) -> None:
    if duration is not None and not isinstance(duration, float):
        raise TypeError("duration must be a float or None")
    if duration is not None and duration < 0:
        raise ValueError("duration must be non-negative")

def validate_data_string(data: str, name: str = "data") -> None:
    if not data or not isinstance(data, str):
        raise ValueError(f"{name} must be a non-empty string")

def validate_optional_int(value: Optional[int], name: str) -> None:
    if value is not None and not isinstance(value, int):
        raise TypeError(f"{name} must be an int or None")

def validate_optional_float(value: Optional[float], name: str) -> None:
    if value is not None and not isinstance(value, float):
        raise TypeError(f"{name} must be a float or None")

def validate_file_data(data: Union[str, bytes]) -> None:
    if data is None:
        raise ValueError("file data cannot be None")
    if isinstance(data, str) and not data.strip():
        raise ValueError("file data string cannot be empty")

def validate_file_source_type(source_type: Optional[str]) -> None:
    if source_type is not None and not isinstance(source_type, str):
        raise TypeError("source_type must be a string or None")