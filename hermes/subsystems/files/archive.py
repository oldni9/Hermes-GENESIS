"""
===============================================================================
Hermes Archive Service
===============================================================================
"""

from __future__ import annotations

import shutil

from pathlib import Path


class FileArchive:

    # ---------------------------------------------------------

    def zip(

        self,

        source: str,

        destination: str,

    ) -> str:

        source = str(Path(source))

        destination = str(Path(destination))

        return shutil.make_archive(

            destination,

            "zip",

            source,

        )

    # ---------------------------------------------------------

    def unpack(

        self,

        archive: str,

        destination: str,

    ) -> None:

        shutil.unpack_archive(

            archive,

            destination,

        )

    # ---------------------------------------------------------

    def supported_formats(self) -> list[str]:

        return sorted(

            shutil.get_archive_formats()

        )