from mkdocs.contrib.search.search_index import ContentSection

class TestContentSection:
    """Tests for ContentSection dataclass equality."""

    def test_content_section_equality(self):
        """Test equality of two identical ContentSection instances."""
        section1 = ContentSection(
            title="Test Section",
            text=["This is some test content.", "More content here."]
        )
        section2 = ContentSection(
            title="Test Section",
            text=["This is some test content.", "More content here."]
        )

        assert section1 == section2

    def test_content_section_inequality(self):
        """Test inequality of two different ContentSection instances."""
        section1 = ContentSection(
            title="Test Section",
            text=["This is some test content."]
        )
        section2 = ContentSection(
            title="Different Section",
            text=["This is some other content."]
        )

        assert section1 != section2

    def test_content_section_inequality_different_text(self):
        """Test inequality of two ContentSection instances with different text."""
        section1 = ContentSection(
            title="Test Section",
            text=["This is some test content."]
        )
        section2 = ContentSection(
            title="Test Section",
            text=["This is different content."]
        )

        assert section1 != section2

    def test_content_section_inequality_different_title(self):
        """Test inequality of two ContentSection instances with different titles."""
        section1 = ContentSection(
            title="Test Section One",
            text=["This is some test content."]
        )
        section2 = ContentSection(
            title="Test Section Two",
            text=["This is some test content."]
        )

        assert section1 != section2


if __name__ == '__main__':
    import pytest
    pytest.main()
