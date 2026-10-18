import pandas as pd
import pytest

from propertyiq.storage.base import Repository
from propertyiq.storage.sqlite_repo import SQLiteRepository


def test_repository_is_abstract():
    with pytest.raises(TypeError):
        Repository()


@pytest.fixture
def repo(tmp_path):
    return SQLiteRepository(tmp_path / "test.db")


def test_save_then_load_round_trips(repo):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"], "c": [1.5, None]})
    repo.save("t", df)
    pd.testing.assert_frame_equal(repo.load("t"), df)


def test_save_replaces_existing(repo):
    repo.save("t", pd.DataFrame({"a": [1, 2, 3]}))
    repo.save("t", pd.DataFrame({"a": [9]}))
    assert len(repo.load("t")) == 1


def test_list_datasets_is_sorted(repo):
    repo.save("b", pd.DataFrame({"a": [1]}))
    repo.save("a", pd.DataFrame({"a": [1]}))
    assert repo.list_datasets() == ["a", "b"]


def test_list_datasets_empty(repo):
    assert repo.list_datasets() == []


def test_load_missing_raises_key_error(repo):
    with pytest.raises(KeyError):
        repo.load("nope")


@pytest.mark.parametrize("bad", ["x; DROP TABLE y", "a b", "", "1abc", 'q"q'])
def test_rejects_unsafe_names(repo, bad):
    with pytest.raises(ValueError):
        repo.save(bad, pd.DataFrame({"a": [1]}))


def test_creates_missing_parent_folder(tmp_path):
    repo = SQLiteRepository(tmp_path / "deep" / "er" / "w.db")
    repo.save("t", pd.DataFrame({"a": [1]}))
    assert repo.list_datasets() == ["t"]


def test_save_does_not_modify_input(repo):
    df = pd.DataFrame({"a": [1]})
    repo.save("t", df)
    assert list(df.columns) == ["a"]
