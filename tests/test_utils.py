import pytest
from pathlib import Path

from manifest.utils import (
    is_async_callable,
    get_by_dot_path,
    set_by_dot_path,
    unset_by_dot_path,
    current_directory,
    import_from_string,
    merge_dicts_flat,
    merge_dicts,
    get_filename_suffix,
    coerce_to_basic_types,
)


def test_is_async_callable():
    async def async_func():
        pass

    def sync_func():
        pass

    assert is_async_callable(async_func)
    assert not is_async_callable(sync_func)


def test_get_by_dot_path():
    data = {"a": {"b": {"c": 3}}}

    assert get_by_dot_path(data, "a.b.c") == 3
    assert get_by_dot_path(data, "a.b.d", default=5) == 5
    assert get_by_dot_path(data, "a.d", default=10) == 10

    with pytest.raises(AssertionError):
        get_by_dot_path([1, 2, 3], "0")


def test_set_by_dot_path():
    data = {"a": {"b": {"c": 3}}}

    assert set_by_dot_path(data, "a.b.c", 4) == {"a": {"b": {"c": 4}}}
    assert set_by_dot_path(data, "a.b.d", 5) == {"a": {"b": {"c": 4, "d": 5}}}
    assert set_by_dot_path(data, "a.e.f", 6) == {"a": {"b": {"c": 4, "d": 5}, "e": {"f": 6}}}

    with pytest.raises(AssertionError):
        set_by_dot_path([1, 2, 3], "0", 4)


def test_unset_by_dot_path():
    data = {"a": {"b": {"c": 3}}}

    assert unset_by_dot_path(data, "a.b.c") == {"a": {"b": {}}}
    assert unset_by_dot_path(data, "a.b") == {"a": {}}
    assert unset_by_dot_path(data, "a") == {}

    with pytest.raises(AssertionError):
        unset_by_dot_path([1, 2, 3], "0")

    assert unset_by_dot_path({"a": 1}, "b.c") == {"a": 1}


def test_current_directory(tmpdir):
    tmp_dir = Path(tmpdir)
    cwd = Path.cwd()

    # Test the happy path
    with current_directory(tmp_dir):
        assert Path.cwd() == tmp_dir

    assert Path.cwd() == cwd

    # Test the unhappy path - non-existent directory
    with pytest.raises(ValueError):
        with current_directory(Path("nonexistent")):
            pass

    # Test the unhappy path - not a directory
    file_path = Path(tmpdir) / "file.txt"
    file_path.touch()

    with pytest.raises(ValueError):
        with current_directory(file_path):
            pass


def test_import_from_string():
    module_path = "os.path"
    class_name = "join"
    func = import_from_string(f"{module_path}.{class_name}")

    def _():
        pass

    assert type(func) == type(_)

    with pytest.raises(ImportError):
        import_from_string("nonexistent.module")

    with pytest.raises(ImportError):
        import_from_string("https://hello.com")

    with pytest.raises(ImportError):
        import_from_string("os.path.nonexistent")

    with pytest.raises(ImportError):
        import_from_string(" hello world!")


def test_merge_dicts_flat():
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    dict3 = {"d": 5}

    merged_dict = merge_dicts_flat(dict1, dict2, dict3)

    assert merged_dict == {"a": 1, "b": 3, "c": 4, "d": 5}


def test_merge_dicts():
    dict1 = {"a": {"b": {"c": "1"}}}
    dict2 = {"a": {"b": {"d": "2"}}}
    dict3 = {"a": {"e": {"f": "3"}}}

    merged_dict = merge_dicts(dict1, dict2, dict3)

    expected_dict = {
        "a": {
            "b": {"c": "1", "d": "2"},
            "e": {"f": "3"}
        }
    }

    assert merged_dict == expected_dict


def test_get_filename_suffix():
    file_path = "path/to/file.txt"
    suffix = get_filename_suffix(file_path)

    assert suffix == ".txt"


def test_coerce_to_basic_types():
    class CustomClass:
        def __init__(self):
            self.a = 1
            self.b = "text"
            self.c = {"x": 1, "y": 2}

    data = [
        1,
        2.5,
        True,
        "text",
        [1, 2, 3],
        {"a": 1, "b": 2},
        CustomClass(),
    ]

    expected_result = [
        1,
        2.5,
        True,
        "text",
        [1, 2, 3],
        {"a": 1, "b": 2},
        {"a": 1, "b": "text", "c": {"x": 1, "y": 2}},
    ]

    coerced_data = coerce_to_basic_types(data)

    assert coerced_data == expected_result
