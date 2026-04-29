"""
Tests for GET / (root) endpoint and redirects.
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirect(self, client):
        """
        Test that GET / redirects to /static/index.html.
        """
        # Follow redirects to get the final response
        response = client.get("/", follow_redirects=True)
        
        # Should eventually get a 200 response
        assert response.status_code == 200
        # Response should contain HTML content
        assert "Mergington High School" in response.text or \
               "<!DOCTYPE html>" in response.text or \
               "<html" in response.text

    def test_root_redirect_location(self, client):
        """
        Test that GET / returns a redirect response with correct location.
        """
        response = client.get("/", follow_redirects=False)
        
        # Should be a redirect (3xx status code)
        assert response.status_code in [301, 302, 303, 307, 308]
        
        # Check location header
        assert "location" in response.headers
        assert "/static/index.html" in response.headers["location"]

    def test_root_accessible(self, client):
        """
        Test that the root endpoint is accessible (doesn't throw 404 or 500).
        """
        response = client.get("/")
        
        # Should not be 404 or 500
        assert response.status_code != 404
        assert response.status_code != 500
