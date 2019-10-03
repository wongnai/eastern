from pathlib import Path

import pytest

from eastern import formatter

TEST_ROOT = (Path(__file__).parents[1]) / "test_data" / "overrides"


def assert_format_equal(file_1, file_2, env={}):
    result = formatter.format(file_1, env)

    if not isinstance(file_2, Path):
        file_2 = Path(file_2)

    assert result == file_2.read_text()


def test_load():
    assert_format_equal(
        TEST_ROOT / "load" / "load.yaml", TEST_ROOT / "load" / "expect.yaml"
    )


def test_load_env():
    assert_format_equal(
        TEST_ROOT / "load_env" / "load.yaml",
        TEST_ROOT / "load_env" / "expect.yaml",
        env={"NAMESPACE": "default"},
    )


def test_load_required():
    assert_format_equal(
        TEST_ROOT / "load_required" / "load.yaml",
        TEST_ROOT / "load_required" / "expect.yaml",
    )


def test_load_required_not_found():
    with pytest.raises(OSError):
        result = formatter.format(TEST_ROOT / "load_required_not_found" / "load.yaml")


def test_load_default_file():
    assert_format_equal(
        TEST_ROOT / "load_default" / "load.yaml",
        TEST_ROOT / "load_default" / "expect.yaml",
    )


def test_load_not_exists():
    assert_format_equal(
        TEST_ROOT / "load_not_exists" / "load.yaml",
        TEST_ROOT / "load_not_exists" / "expect.yaml",
        env={"NAMESPACE": "notexists"},
    )
