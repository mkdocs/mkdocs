"""
Mutation tests for mkdocs/utils/__init__.py.

I couldn't get this to work from here so I put it in a root tests/ directory.
"""

import pytest
from mkdocs.utils import (
    get_relative_url,
)


class TestGetRelativeUrl:
    """Tests for get_relative_url function."""

    def test_get_relative_url_same_directory(self):
        """Test relative URL in same directory."""
        result = get_relative_url('page.html', 'index.html')
        assert result == 'page.html'

    def test_get_relative_url_parent_directory(self):
        """Test relative URL to parent directory."""
        result = get_relative_url('page.html', 'sub/index.html')
        assert result == '../page.html'


if __name__ == '__main__':
    pytest.main()
