# Unit Testing I (Extend Coverage)

import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from mkdocs.config.base import BaseConfigOption
from mkdocs.utils import get_build_datetime, get_build_timestamp


class EdgeCaseTests(unittest.TestCase):
    """Test edge cases and error conditions with low coverage."""

    def test_config_option_mutable_default_copy(self):
        """Test BaseConfigOption default property with mutable values.

        Ensures mutable defaults are properly copied to prevent
        shared state between config instances.
        """
        option = BaseConfigOption()
        # Test with mutable default (list)
        option._default = ['item1', 'item2']

        default1 = option.default
        default2 = option.default

        # Verify copies are independent
        default1.append('item3')
        self.assertEqual(option._default, ['item1', 'item2'])
        self.assertEqual(default2, ['item1', 'item2'])
        self.assertNotEqual(default1, default2)

    def test_config_option_immutable_default(self):
        """Test BaseConfigOption default property with immutable values.

        When default value doesn't have copy() method (immutable types).
        """
        option = BaseConfigOption()
        # Test with immutable default (string)
        option._default = 'immutable_string'

        default1 = option.default
        default2 = option.default

        # Should return same object for immutable types
        self.assertEqual(default1, 'immutable_string')
        self.assertEqual(default2, 'immutable_string')

    def test_build_datetime_with_source_date_epoch(self):
        """Test get_build_datetime with SOURCE_DATE_EPOCH environment variable.

        Reproducible builds using SOURCE_DATE_EPOCH for timestamp.
        """
        # Test with valid SOURCE_DATE_EPOCH
        test_timestamp = '1609459200'  # 2021-01-01 00:00:00 UTC
        with patch.dict(os.environ, {'SOURCE_DATE_EPOCH': test_timestamp}):
            result = get_build_datetime()
            expected = datetime.fromtimestamp(int(test_timestamp), timezone.utc)
            self.assertEqual(result, expected)
            self.assertEqual(result.tzinfo, timezone.utc)

    def test_build_datetime_without_source_date_epoch(self):
        """Test get_build_datetime without SOURCE_DATE_EPOCH.

        Normal build without reproducible build environment.
        """
        # Ensure SOURCE_DATE_EPOCH is not set
        with patch.dict(os.environ, {}, clear=True):
            with patch('mkdocs.utils.datetime') as mock_datetime:
                mock_now = MagicMock()
                mock_datetime.now.return_value = mock_now
                mock_datetime.timezone = timezone

                result = get_build_datetime()

                mock_datetime.now.assert_called_once_with(timezone.utc)
                self.assertEqual(result, mock_now)

    def test_build_timestamp_with_empty_pages(self):
        """Test get_build_timestamp with empty pages list.

        When no pages are provided, should fall back to build datetime.
        """
        with patch('mkdocs.utils.get_build_datetime') as mock_get_build_datetime:
            mock_datetime = datetime(2021, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_get_build_datetime.return_value = mock_datetime

            # Test with None pages (empty)
            result = get_build_timestamp(pages=None)

            mock_get_build_datetime.assert_called_once()
            expected_timestamp = int(mock_datetime.timestamp())
            self.assertEqual(result, expected_timestamp)

    def test_config_option_set_on_non_config_object(self):
        """Test BaseConfigOption.__set__ with invalid parent object.

        Attempting to set config option on non-Config object should raise AttributeError.
        """
        from mkdocs.config.base import Config

        option = BaseConfigOption()
        option._name = 'test_option'

        # Test setting on wrong object type
        wrong_object = {'not': 'a_config'}

        with self.assertRaises(AttributeError) as context:
            option.__set__(wrong_object, 'some_value')

        error_msg = str(context.exception)
        self.assertIn('test_option', error_msg)
        self.assertIn('dict', error_msg)
        self.assertIn('Config', error_msg)


if __name__ == '__main__':
    unittest.main()
