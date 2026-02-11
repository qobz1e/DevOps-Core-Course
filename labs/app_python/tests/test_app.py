"""
Unit tests for DevOps Info Service
"""
import json
import pytest
from app import app, START_TIME, get_uptime, get_system_info

def test_main_endpoint_structure(client):
    """Test that main endpoint returns correct JSON structure."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = json.loads(response.data)
    
    # Check service section
    assert 'service' in data
    assert data['service']['name'] == 'devops-info-service'
    assert data['service']['version'] == '2.0.0'
    assert data['service']['framework'] == 'Flask'
    
    # Check system section
    assert 'system' in data
    assert 'hostname' in data['system']
    assert 'platform' in data['system']
    assert 'python_version' in data['system']
    assert 'is_docker_container' in data['system']
    
    # Check runtime section
    assert 'runtime' in data
    assert 'uptime_seconds' in data['runtime']
    assert 'uptime_human' in data['runtime']
    assert 'current_time' in data['runtime']
    
    # Check endpoints list
    assert 'endpoints' in data
    assert len(data['endpoints']) >= 3
    endpoints = {e['path']: e for e in data['endpoints']}
    assert '/' in endpoints
    assert '/health' in endpoints
    assert '/docker' in endpoints

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'uptime_seconds' in data
    assert 'environment' in data
    assert 'container_id' in data or data['container_id'] is None

def test_docker_endpoint(client):
    """Test Docker info endpoint."""
    response = client.get('/docker')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'is_docker' in data
    assert 'container_id' in data
    assert 'message' in data
    
    # Since we're testing locally, is_docker should be False
    assert data['is_docker'] is False
    assert data['message'] == 'Running locally'

def test_404_error_handler(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert data['error'] == 'Not Found'
    assert 'available_endpoints' in data
    assert len(data['available_endpoints']) >= 3

def test_uptime_calculation():
    """Test uptime calculation function."""
    from app import get_uptime
    
    uptime = get_uptime()
    assert 'seconds' in uptime
    assert 'human' in uptime
    assert isinstance(uptime['seconds'], int)
    assert isinstance(uptime['human'], str)
    assert uptime['seconds'] >= 0
    
    # Test human readable format
    if uptime['seconds'] > 0:
        assert 'second' in uptime['human'] or 'minute' in uptime['human'] or 'hour' in uptime['human']

def test_system_info():
    """Test system information collection."""
    from app import get_system_info
    
    info = get_system_info()
    assert 'hostname' in info
    assert 'platform' in info
    assert 'architecture' in info
    assert 'cpu_count' in info
    assert 'python_version' in info
    assert 'is_docker_container' in info
    assert info['cpu_count'] > 0
    assert isinstance(info['hostname'], str)
    assert len(info['hostname']) > 0

def test_main_endpoint_required_fields(client):
    """Test that main endpoint contains all required fields from Lab 1 spec."""
    response = client.get('/')
    data = json.loads(response.data)
    
    # Required fields from Lab 1 specification
    assert data['service']['name'] is not None
    assert data['service']['version'] is not None
    assert data['service']['framework'] is not None
    assert data['system']['hostname'] is not None
    assert data['runtime']['timezone'] == 'UTC'
    assert len(data['endpoints']) > 0

def test_request_info(client):
    """Test that request information is captured correctly."""
    response = client.get('/', headers={'User-Agent': 'pytest-test-agent'})
    data = json.loads(response.data)
    
    assert data['request']['method'] == 'GET'
    assert data['request']['path'] == '/'
    assert data['request']['user_agent'] == 'pytest-test-agent'
    assert data['request']['client_ip'] is not None

def test_health_check_always_200(client):
    """Test that health endpoint always returns 200 OK."""
    response = client.get('/health')
    assert response.status_code == 200
    
    # Multiple requests should still work
    for _ in range(5):
        response = client.get('/health')
        assert response.status_code == 200
        assert json.loads(response.data)['status'] == 'healthy'

def test_system_info_consistent_with_endpoint(client):
    """Test that get_system_info() matches what's returned by the endpoint."""
    from app import get_system_info
    
    # Get data from function
    system_info_func = get_system_info()
    
    # Get data from endpoint
    response = client.get('/')
    data = json.loads(response.data)
    system_info_endpoint = data['system']
    
    # Compare key fields
    assert system_info_func['hostname'] == system_info_endpoint['hostname']
    assert system_info_func['platform'] == system_info_endpoint['platform']
    assert system_info_func['python_version'] == system_info_endpoint['python_version']
    assert system_info_func['cpu_count'] == system_info_endpoint['cpu_count']