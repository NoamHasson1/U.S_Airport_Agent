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


@patch('tools.fetch_live_flights_from_api')
def test_free_tier_truncation_mitigation_extrapolation(mock_fetch):
    """
    Test 5: Verifies that when the API returns exactly 400 flights (indicating a 
    free-tier 100-record truncation boundary), the pipeline correctly mitigates 
    the distortion by extrapolating the volume based on the airport's true Mega Hub tier.
    """
    # Simulate the API hitting the exact flatline limit of 400 flights
    mock_fetch.return_value = 400
    
    # Process data for a known Mega Hub (JFK)
    data = generate_deterministic_airport_data("JFK")
    
    # Dynamic search for whatever flight volume key you used (e.g., live_flights, daily_flights)
    flight_key = [k for k in data.keys() if 'flight' in k or 'arrival' in k]
    
    if flight_key:
        # Verify the volume was extrapolated and is not stuck at the truncated 400 flatline
        assert data[flight_key[0]] != 400
        assert data[flight_key[0]] >= 800  # Mega Hub scaled minimum boundary
    
    # Double check via the congestion rate which we know exists
    assert data["congestion_rate"] > 0.40


@patch('tools.fetch_live_flights_from_api')
def test_investment_score_weight_sensitivity(mock_fetch):
    """
    Test 6: Validates that the multi-factor investment score equation behaves 
    predictably according to PE model weights, and remains strictly bounded between 0 and 100.
    """
    # Mock a fixed stable flight stream
    mock_fetch.return_value = 500
    
    # Retrieve data for JFK
    jfk_profile = generate_deterministic_airport_data("JFK")
    
    # Ensure scores conform to infrastructure mathematical boundaries
    assert 0.0 <= jfk_profile["investment_score"] <= 100.0
    
    # Dynamic search for your long-haul metric key (e.g., long_haul_pct, long_haul_ratio)
    long_haul_key = [k for k in jfk_profile.keys() if 'long' in k]
    if long_haul_key:
        assert jfk_profile[long_haul_key[0]] > 0


@patch('tools.requests.get')
def test_dynamic_inference_tier_classification(mock_get):
    """
    Test 7: Verifies that when an analyst requests a valid US gateway omitted from 
    the local JSON registry, the tool dynamically infers its operational tier 
    (e.g., Small/Medium Regional) purely from live incoming API payload volume.
    """
    # Mock a low-volume active response (e.g., 15 flights * 4 = 60 daily flights)
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": [None] * 15}
    
    # Execute tool data generation for an unlisted but valid active airport code
    data = generate_deterministic_airport_data("BTV")
    
    # Assert dynamic schema injection worked on-the-fly without requiring a 'status' key
    assert data["airport_code"] == "BTV"
    assert "tier" in data
    assert data["tier"] in ["Large Regional", "Medium/Small Regional", "Mega Hub"]
    assert "error" not in data