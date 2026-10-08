from __future__ import annotations

from importlib.metadata import version
from importlib.resources import files

import elmo_sdk
from elmo_sdk import __version__


def test_reports_the_version_it_is_installed_as() -> None:
    assert __version__ == version("elmo-sdk")


def test_says_it_is_typed() -> None:
    assert files(elmo_sdk).joinpath("py.typed").is_file()
