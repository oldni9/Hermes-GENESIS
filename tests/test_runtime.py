# tests/test_runtime.py

"""
===============================================================================
Hermes Genesis

Runtime Integration Test

Author:
    Aryan + ChatGPT
===============================================================================
"""

from hermes import Hermes


def test_runtime_pipeline() -> None:
    """
    Verify the complete runtime pipeline.
    """

    hermes = Hermes()

    hermes.start()

    try:

        response = hermes.run("Hello Hermes")

        assert response is not None

        assert response.success is True

        assert response.data is not None

    finally:

        hermes.shutdown()


if __name__ == "__main__":

    test_runtime_pipeline()

    print("Runtime pipeline test passed.")