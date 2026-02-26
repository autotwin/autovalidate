# tests/test_delete_files.py

import os
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from autovalidate.delete_files import confirm_deletions


def test_confirm_deletions_yes_deletes_file_and_dir(tmp_path, monkeypatch):
    """Test that answering 'y' correctly deletes both files and directories."""
    
    # 1. Setup a dummy file and directory
    dummy_file = tmp_path / "test_file.txt"
    dummy_file.write_text("hello")
    
    dummy_dir = tmp_path / "test_dir"
    dummy_dir.mkdir()
    (dummy_dir / "nested.txt").write_text("world")
    
    assert dummy_file.exists()
    assert dummy_dir.exists()

    # 2. Mock input() to always return 'y'
    inputs = iter(['y', 'yes'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # 3. Run function
    results = confirm_deletions(dummy_file, dummy_dir)

    # 4. Verify everything was deleted
    assert results[dummy_file] is True
    assert results[dummy_dir] is True
    assert not dummy_file.exists()
    assert not dummy_dir.exists()


def test_confirm_deletions_no_skips_deletion(tmp_path, monkeypatch):
    """Test that answering 'n' or empty string leaves files intact."""
    
    dummy_file = tmp_path / "keep_me.txt"
    dummy_file.write_text("keep")
    
    # Mock input() to return 'n' first, then '' (empty string for default No)
    inputs = iter(['n', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    results = confirm_deletions(dummy_file, dummy_file)

    assert results[dummy_file] is False
    assert dummy_file.exists()


def test_confirm_deletions_non_existent_path(monkeypatch):
    """Test that a 'y' on a non-existent path doesn't crash the script."""
    
    fake_path = Path("does_not_exist_anywhere.txt")
    
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    
    results = confirm_deletions(fake_path)
    
    assert results[fake_path] is False


def test_confirm_deletions_invalid_input_retry(tmp_path, monkeypatch):
    """Test that the script asks again if you type junk."""
    
    dummy_file = tmp_path / "retry.txt"
    dummy_file.write_text("stuff")
    
    # User types junk, then 'x', then finally 'y'
    inputs = iter(['junk', 'x', 'y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    results = confirm_deletions(dummy_file)

    assert results[dummy_file] is True
    assert not dummy_file.exists()

