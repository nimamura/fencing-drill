"""Tests for OGP (Open Graph Protocol) and Twitter Card meta tags."""
import os
import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class TestOGPMetaTags:
    """Tests for Open Graph meta tags."""

    def test_og_title_exists(self):
        """Page should have og:title meta tag."""
        response = client.get("/")
        assert response.status_code == 200
        content = response.text
        assert 'property="og:title"' in content, "og:title meta tag should exist"

    def test_og_description_exists(self):
        """Page should have og:description meta tag."""
        response = client.get("/")
        content = response.text
        assert 'property="og:description"' in content, "og:description meta tag should exist"

    def test_og_image_exists(self):
        """Page should have og:image meta tag."""
        response = client.get("/")
        content = response.text
        assert 'property="og:image"' in content, "og:image meta tag should exist"

    def test_og_url_exists(self):
        """Page should have og:url meta tag."""
        response = client.get("/")
        content = response.text
        assert 'property="og:url"' in content, "og:url meta tag should exist"

    def test_og_type_exists(self):
        """Page should have og:type meta tag."""
        response = client.get("/")
        content = response.text
        assert 'property="og:type"' in content, "og:type meta tag should exist"

    def test_og_site_name_exists(self):
        """Page should have og:site_name meta tag."""
        response = client.get("/")
        content = response.text
        assert 'property="og:site_name"' in content, "og:site_name meta tag should exist"

    def test_og_image_dimensions_exist(self):
        """Page should have og:image:width and og:image:height meta tags."""
        response = client.get("/")
        content = response.text
        assert 'property="og:image:width"' in content, "og:image:width meta tag should exist"
        assert 'property="og:image:height"' in content, "og:image:height meta tag should exist"


class TestTwitterCardMetaTags:
    """Tests for Twitter Card meta tags."""

    def test_twitter_card_exists(self):
        """Page should have twitter:card meta tag."""
        response = client.get("/")
        content = response.text
        assert 'name="twitter:card"' in content, "twitter:card meta tag should exist"

    def test_twitter_title_exists(self):
        """Page should have twitter:title meta tag."""
        response = client.get("/")
        content = response.text
        assert 'name="twitter:title"' in content, "twitter:title meta tag should exist"

    def test_twitter_description_exists(self):
        """Page should have twitter:description meta tag."""
        response = client.get("/")
        content = response.text
        assert 'name="twitter:description"' in content, "twitter:description meta tag should exist"

    def test_twitter_image_exists(self):
        """Page should have twitter:image meta tag."""
        response = client.get("/")
        content = response.text
        assert 'name="twitter:image"' in content, "twitter:image meta tag should exist"


class TestOGPImage:
    """Tests for OGP image file."""

    def test_og_image_file_exists(self):
        """OGP image file should exist in static/images directory."""
        og_image_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "images", "og-image.png"
        )
        assert os.path.exists(og_image_path), "static/images/og-image.png should exist"

    def test_og_image_is_accessible(self):
        """OGP image should be accessible via HTTP."""
        response = client.get("/static/images/og-image.png")
        assert response.status_code == 200, "OGP image should be accessible"
        assert response.headers["content-type"] == "image/png", "OGP image should be PNG"
