# examples/basic_chat.py

"""
===============================================================================
Hermes Genesis

Basic Chat Example

Author:
    Aryan + ChatGPT
===============================================================================
"""

from hermes import Hermes


def main() -> None:

    hermes = Hermes()

    hermes.start()

    print("Hermes Genesis")
    print("Type 'exit' to quit.\n")

    try:

        while True:

            prompt = input("You > ").strip()

            if prompt.lower() in {
                "exit",
                "quit",
            }:
                break

            response = hermes.run(prompt)

            print(f"\nHermes > {response.text}")

            if response.data:

                print(response.data)

            print()

    finally:

        hermes.shutdown()


if __name__ == "__main__":

    main()
