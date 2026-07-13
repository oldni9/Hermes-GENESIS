# hermes/main.py

"""
===============================================================================
Hermes Genesis

Application Entry Point

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes import Hermes


def main() -> None:
    """
    Hermes application entry.
    """

    hermes = Hermes()

    hermes.start()

    try:

        while True:

            prompt = input(">>> ").strip()

            if not prompt:
                continue

            if prompt.lower() in {
                "exit",
                "quit",
            }:
                break

            response = hermes.run(prompt)

            print(response.text)

            if response.data is not None:

                print(response.data)

    finally:

        hermes.shutdown()


if __name__ == "__main__":

    main()