"""
===============================================================================
Hermes File Search Service
===============================================================================
"""

from __future__ import annotations

import fnmatch
import re

from pathlib import Path


class FileSearch:

    # ------------------------------------------------------------------

    def by_name(
        self,
        root: str,
        pattern: str,
    ) -> list[Path]:

        return list(Path(root).rglob(pattern))

    # ------------------------------------------------------------------

    def by_extension(
        self,
        root: str,
        extension: str,
    ) -> list[Path]:

        extension = extension.lower().lstrip(".")

        return [

            p

            for p in Path(root).rglob("*")

            if p.is_file()

            and p.suffix.lower() == f".{extension}"

        ]

    # ------------------------------------------------------------------

    def glob(
        self,
        root: str,
        pattern: str,
    ) -> list[Path]:

        return list(Path(root).glob(pattern))

    # ------------------------------------------------------------------

    def recursive_glob(
        self,
        root: str,
        pattern: str,
    ) -> list[Path]:

        return list(Path(root).rglob(pattern))

    # ------------------------------------------------------------------

    def regex(
        self,
        root: str,
        expression: str,
    ) -> list[Path]:

        regex = re.compile(expression)

        return [

            p

            for p in Path(root).rglob("*")

            if regex.search(p.name)

        ]

    # ------------------------------------------------------------------

    def contains(
        self,
        root: str,
        text: str,
    ) -> list[Path]:

        text = text.lower()

        matches: list[Path] = []

        for p in Path(root).rglob("*"):

            if text in p.name.lower():

                matches.append(p)

        return matches

    # ------------------------------------------------------------------

    def wildcard(
        self,
        root: str,
        pattern: str,
    ) -> list[Path]:

        return [

            p

            for p in Path(root).rglob("*")

            if fnmatch.fnmatch(

                p.name,

                pattern,

            )

        ]