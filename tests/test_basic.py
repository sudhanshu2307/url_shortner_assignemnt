# tests/test.py
import pytest
from app.main import app, url_store, store_lock  # Import url_store and store_lock for testing
from app.models import URLMapping
import json


@pytest.fixture
def client():
    # Configure app for testing
    app.config['TESTING'] = True
    # Clear the url_store before each test to ensure a clean state
    with store_lock:
        url_store.clear()
    with app.test_client() as client:
        yield client


# --- Provided Test ---
def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'


# --- New Tests for Core Functionality ---

def test_shorten_url_success(client):
    """Test successful URL shortening."""
    long_url = "https://www.example.com/very/long/url/for/testing"
    response = client.post('/api/shorten', json={'url': long_url})

    assert response.status_code == 201  # Created
    data = response.get_json()
    assert "short_code" in data
    assert "short_url" in data
    assert len(data['short_code']) == 6  # Short code length check
    assert data['short_url'].startswith(f"http://localhost:5000/{data['short_code']}")

    # Verify it's stored in our in-memory store
    with store_lock:
        assert data['short_code'] in url_store
        stored_mapping = url_store[data['short_code']]
        assert stored_mapping.original_url == long_url
        assert stored_mapping.clicks == 0


def test_shorten_url_invalid_input(client):
    """Test shortening with invalid or missing URL."""
    # Missing 'url' key
    response = client.post('/api/shorten', json={'wrong_key': 'http://test.com'})
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Invalid URL format
    response = client.post('/api/shorten', json={'url': 'not-a-valid-url'})
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Empty URL
    response = client.post('/api/shorten', json={'url': ''})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_redirect_success_and_click_count(client):
    """Test successful redirection and click count increment."""
    long_url = "https://www.another-example.org/path/to/resource"
    short_response = client.post('/api/shorten', json={'url': long_url})
    short_code = short_response.get_json()['short_code']

    # First redirection
    redirect_response_1 = client.get(f'/{short_code}')
    assert redirect_response_1.status_code == 302  # Found (redirect)
    assert redirect_response_1.headers['Location'] == long_url

    # Check stats after first click
    stats_response_1 = client.get(f'/api/stats/{short_code}')
    assert stats_response_1.status_code == 200
    assert stats_response_1.get_json()['clicks'] == 1

    # Second redirection
    redirect_response_2 = client.get(f'/{short_code}')
    assert redirect_response_2.status_code == 302
    assert redirect_response_2.headers['Location'] == long_url

    # Check stats after second click
    stats_response_2 = client.get(f'/api/stats/{short_code}')
    assert stats_response_2.status_code == 200
    assert stats_response_2.get_json()['clicks'] == 2


def test_redirect_not_found(client):
    """Test redirection for a non-existent short code."""
    response = client.get('/nonexistent1')
    assert response.status_code == 404  # Not Found


def test_get_stats_success(client):
    """Test retrieving stats for an existing short code."""
    long_url = "https://www.google.com"
    short_response = client.post('/api/shorten', json={'url': long_url})
    short_code = short_response.get_json()['short_code']

    # Simulate a few clicks
    client.get(f'/{short_code}')
    client.get(f'/{short_code}')

    stats_response = client.get(f'/api/stats/{short_code}')
    assert stats_response.status_code == 200
    data = stats_response.get_json()
    assert data['url'] == long_url
    assert data['clicks'] == 2
    assert "created_at" in data


def test_get_stats_not_found(client):
    """Test retrieving stats for a non-existent short code."""
    response = client.get('/api/stats/nonexistent2')
    assert response.status_code == 404


def test_shorten_existing_url_returns_same_short_code(client):
    """
    Test that attempting to shorten an already shortened URL returns the
    existing short code (to avoid creating duplicates unnecessarily).
    """
    long_url = "https://www.example.com/unique-url-for-duplicate-test"

    # First time shortening
    response1 = client.post('/api/shorten', json={'url': long_url})
    assert response1.status_code == 201
    short_code1 = response1.get_json()['short_code']

    # Second time shortening the exact same URL
    response2 = client.post('/api/shorten', json={'url': long_url})
    assert response2.status_code == 200  # Should return OK (not Created)
    short_code2 = response2.get_json()['short_code']

    assert short_code1 == short_code2  # Should be the same short code

    # Verify only one entry in store (implies no new short code was generated)
    with store_lock:
        count = sum(1 for mapping in url_store.values() if mapping.original_url == long_url)
        assert count == 1