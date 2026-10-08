from __future__ import annotations

import pytest

from elmo_sdk import Elmo


@pytest.mark.live
def test_runs_the_readme_usage_example() -> None:
    elmo = Elmo()
    data = elmo.brands.list()
    print(data)
