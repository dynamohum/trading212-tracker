import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from app import create_app
from app.config import Config

@pytest.fixture
def client():
    # Create a temp file for the DB
    db_fd, db_path = tempfile.mkstemp()
    
    # Create a test config class
    class TestConfig(Config):
        DB_FILE = db_path
        TESTING = True

    # Patch the background tracker so it doesn't run
    with patch('app.services.tracker_service.TrackerService.start_background_tracking'):
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            yield client
            
    # Cleanup temp file
    os.close(db_fd)
    os.unlink(db_path)

@patch('app.routes.api.t212_service')
def test_get_positions(mock_service, client):
    """GET /api/positions returns list of positions"""
    # Setup Mock
    mock_client = MagicMock()
    mock_service.get_client.return_value = mock_client
    mock_service.mode = 'demo'
    
    expected_items = [
        {"ticker": "AAPL", "quantity": 10, "averagePrice": 150, "currentPrice": 155, "ppl": 50},
        {"ticker": "MSFT", "quantity": 5, "averagePrice": 280, "currentPrice": 290, "ppl": 50}
    ]
    mock_client.get_all_positions.return_value = expected_items
    
    response = client.get('/api/positions')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'items' in data
    assert isinstance(data['items'], list)
    assert len(data['items']) == 2
    assert data['mode'] == 'demo'

def test_get_returns(client):
    """GET /api/returns returns calculate returns object"""
    response = client.get('/api/returns')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, dict)

def test_get_settings(client):
    """GET /api/settings returns application settings"""
    response = client.get('/api/settings')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'tracking' in data
    assert 'hidden_tickers' in data
    assert isinstance(data['hidden_tickers'], list)

def test_update_settings(client):
    """POST /api/settings updates settings successfully"""
    # Toggle tracking to True and add a hidden ticker
    new_settings = {'tracking': True, 'hidden_tickers': ['TSLA']}
    
    response = client.post(
        '/api/settings',
        data=json.dumps(new_settings),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert response.get_json()['status'] == 'updated'
    
    # Verify it changed
    check_response = client.get('/api/settings')
    data = check_response.get_json()
    assert data['tracking'] is True
    assert 'TSLA' in data['hidden_tickers']
