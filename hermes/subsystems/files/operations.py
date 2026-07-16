"""
===============================================================================
Hermes Files Operations
===============================================================================
"""

from __future__ import annotations

import shutil

from pathlib import Path


class FileOperations:

    # ---------------------------------------------------------

    def exists(
        self,
        path: str,
    ) -> bool:

        return Path(path).exists()

    # ---------------------------------------------------------

    def create_folder(
        self,
        path: str,
    ):

        Path(path).mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------

    def create_file(
        self,
        path: str,
    ):

        Path(path).touch(
            exist_ok=True,
        )

    # ---------------------------------------------------------

    def read_text(
        self,
        path: str,
        encoding: str = "utf-8",
    ) -> str:

        return Path(path).read_text(
            encoding=encoding,
        )

    # ---------------------------------------------------------

    def write_text(
        self,
        path: str,
        text: str,
        encoding: str = "utf-8",
    ):

        Path(path).write_text(

            text,

            encoding=encoding,

        )

    # ---------------------------------------------------------

    def append_text(
        self,
        path: str,
        text: str,
        encoding: str = "utf-8",
    ):

        with Path(path).open(

            "a",

            encoding=encoding,

        ) as f:

            f.write(text)

    # ---------------------------------------------------------

    def copy(
        self,
        source: str,
        destination: str,
    ):

        shutil.copy2(

            source,

            destination,

        )

    # ---------------------------------------------------------

    def move(
        self,
        source: str,
        destination: str,
    ):

        shutil.move(

            source,

            destination,

        )

    # ---------------------------------------------------------

    def rename(
        self,
        source: str,
        destination: str,
    ):

        Path(source).rename(destination)

    # ---------------------------------------------------------

    def delete(
        self,
        path: str,
    ):

        p = Path(path)

        if p.is_dir():

            shutil.rmtree(p)

        elif p.exists():

            p.unlink()