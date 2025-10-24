"""
A test cases for mkdocs/utils/__init__.py get_build_timestamp function.
This was wrote after the mutation testing revealed these cases were missing.

Author: Kemoy Campbell
"""
import pytest
from datetime import datetime, timezone
from mkdocs.utils import (
    get_build_timestamp,
    get_build_datetime
)

"""
    A dummy Page class to simulate page with update_date attribute
"""
class DummyPage:
    def __init__(self, update_date):
        self.update_date = update_date

class TestGetBuildTimestamp:
    """Tests for get_build_timestamp function with a collection of pages and dates."""

    def test_get_build_timestamp_pages(self):
        """Test build timestamp from pages with update_date."""
        pages = [
            DummyPage(update_date='2023-01-01T12:00:00Z'),
            DummyPage(update_date='2023-01-02T12:00:00Z'),
            DummyPage(update_date='2023-01-03T12:00:00Z'),
        ]
        result = get_build_timestamp(pages = pages)

        expected_dt = datetime.fromisoformat('2023-01-03T12:00:00+00:00').replace(tzinfo=timezone.utc)

        assert result == int(expected_dt.timestamp())

    """
    Test build timestamp when no pages are provided. We expect the current build datetime.
    """
    def test_get_build_timestamp_no_pages(self):

        result = get_build_timestamp(pages=None)
        expected_dt = get_build_datetime()

        assert result == int(expected_dt.timestamp())


if __name__ == '__main__':
    pytest.main()
