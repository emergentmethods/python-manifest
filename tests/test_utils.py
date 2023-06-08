import pytest
from pathlib import Path

from manifest.utils import (
    is_async_callable,
    DotDict,
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


def test_dot_dict():
    data = {
        "a": 1,
        "b": {"c": 2},
        "d": {"e": {"f": 3}},
        "g": [4, 5],
    }
    dot_dict = DotDict(data)

    assert dot_dict["a"] == 1
    assert dot_dict["b.c"] == 2
    assert dot_dict["b"]["c"] == 2
    assert dot_dict["d.e.f"] == 3
    assert dot_dict["d"]["e"]["f"] == 3
    assert dot_dict["g"] == [4, 5]

    with pytest.raises(KeyError):
        _ = dot_dict["nonexistent"]

    dot_dict["new.key"] = "value"
    assert dot_dict["new.key"] == "value"

    del dot_dict["new.key"]
    with pytest.raises(KeyError):
        _ = dot_dict["new.key"]

    with pytest.raises(KeyError):
        del dot_dict["nonexistent"]

    with pytest.raises(KeyError):
        del dot_dict["d.e.z"]

    assert dot_dict.get("a", None) == 1


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
