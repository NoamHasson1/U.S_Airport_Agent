import pytest
from unittest.mock import patch
import streamlit as st
from tools import generate_deterministic_airport_data, fetch_live_flights_from_api

# --- FIX STREAMLIT CACHE IN TESTING ENVIRONMENT ---
# Prevents Streamlit from throwing runtime errors when calling cached functions outside the browser
st.cache_data.clear()


def test_deterministic_registry_airport():
    """
    Test 1: Ensures that an airport listed in the JSON config (e.g., JFK)
    consistently returns the exact same mathematical profile due to hashing seeds.
    """
    data_run_1 = generate_deterministic_airport_data("JFK")
    data_run_2 = generate_deterministic_airport_data("JFK")
    
    # Assert structural profile mapping
    assert data_run_1["airport_code"] == "JFK"
    assert data_run_1["tier"] == "Mega Hub"
    assert data_run_1["max_capacity_daily"] > 1000
    
    # Assert Absolute Determinism (The core architectural promise)
    assert data_run_1["investment_score"] == data_run_2["investment_score"]
    assert data_run_1["congestion_rate"] == data_run_2["congestion_rate"]


def test_dynamic_inference_for_unlisted_airport():
    """
    Test 2: Ensures that a completely fictional airport code (e.g., XYZ)
    is caught by the Input Accuracy Guard and rejected rather than 
    generating misleading fictional profiles.
    """
    data = generate_deterministic_airport_data("XYZ")
    
    assert data["airport_code"] == "XYZ"
    assert data["status"] == "invalid_airport_code"
    assert "error" in data
    assert "tier" not in data 


@patch('tools.requests.get')
def test_fetch_live_flights_api_success(mock_get):
    """
    Test 3: Mocks a successful 200 OK enterprise response from AirLabs.
    Verifies the daily multiplier scaling logic (live_count * 4).
    """
    # Force the mock configuration to return a dummy list of 50 flights
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": [None] * 50}
    
    # Execute tool function
    simulated_daily_flights = fetch_live_flights_from_api("LAX")
    
    # Verification: 50 real-time flights * 4 (6-hour window scaling multiplier) = 200 daily
    assert simulated_daily_flights == 200


@patch('tools.requests.get')
def test_fetch_live_flights_api_failure_fallback(mock_get):
    """
    Test 4: Mocks a 500 Server Error network crash from AirLabs.
    Verifies that the tool catches the error and cleanly returns None to activate the fallback layer.
    """
    # Simulate a network crash or server failure
    mock_get.side_effect = Exception("Network Timeout Connection Refused")
    
    # Execute tool function - should handle exception internally and return None safely
    result = fetch_live_flights_from_api("SFO")
    
    assert result is None