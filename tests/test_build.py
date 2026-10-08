from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

import pytest
from hatchling.build import build_sdist, build_wheel


def test_builds_a_wheel_from_its_sdist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    source = tmp_path / "source"
    with zipfile.ZipFile(source / build_wheel(str(source))) as archive:
        expected = archive.namelist()
    sdist = build_sdist(str(tmp_path))
    with tarfile.open(tmp_path / sdist) as archive:
        archive.extraction_filter = getattr(tarfile, "data_filter", None)
        archive.extractall(tmp_path)
    monkeypatch.chdir(tmp_path / sdist.removesuffix(".tar.gz"))
    wheel = build_wheel(str(tmp_path))
    with zipfile.ZipFile(tmp_path / wheel) as archive:
        names = archive.namelist()
    assert sorted(set(expected) - set(names)) == []
