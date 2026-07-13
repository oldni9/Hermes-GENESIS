# tests/test_application.py

"""
===============================================================================
Hermes Genesis

Application Integration Test

Author:
    Aryan + ChatGPT
===============================================================================
"""

from hermes import Hermes


def test_application_lifecycle() -> None:
    """
    Verify Hermes application lifecycle.
    """

    hermes = Hermes()

    # --------------------------------------------------------------

    assert hermes.started is False

    # --------------------------------------------------------------

    hermes.start()

    assert hermes.started is True

    # --------------------------------------------------------------

    response = hermes.run(
        "Hello Hermes"
    )

    assert response.success is True

    assert response.data is not None

    # --------------------------------------------------------------

    hermes.shutdown()

    assert hermes.started is False


if __name__ == "__main__":

    test_application_lifecycle()

    print("Application lifecycle test passed.")