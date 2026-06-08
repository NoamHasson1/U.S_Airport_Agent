import hashlib
import json
import os
import random
import requests
import time
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- DYNAMIC CONFIGURATION LOADER ---
CONFIG_FILE = "airport_config.json"
AIRPORT_PROFILES = {}

try:
    with open(CONFIG_FILE, "r") as f:
        AIRPORT_PROFILES = json.load(f)
    print(f"      [System]: Successfully loaded {len(AIRPORT_PROFILES)} static profiles from '{CONFIG_FILE}'.")
except FileNotFoundError:
    print(f"      [System Warning]: '{CONFIG_FILE}' missing. System operating purely via dynamic inference.")
except json.JSONDecodeError:
    print(f"      [System Error]: '{CONFIG_FILE}' contains malformed JSON. Fallback to dynamic inference initiated.")


@st.cache_data(ttl=600)  # <-- Cache API results for 10 minutes to save credits and speed up responses
def fetch_live_flights_from_api(airport_code: str) -> int:
    """
    Calls the commercial AirLabs API to get real-time flight schedules.
    Cached for 10 minutes per airport code to eliminate redundant network hits.
    """
    api_key = os.getenv("AIRLABS_API_KEY")
    if not api_key:
        print("      [AirLabs]: No API Key found in environment variables.")
        return None
        
    airport_code = airport_code.upper().strip()
    url = f"https://airlabs.co/api/v9/schedules?api_key={api_key}&arr_iata={airport_code}"
    
    print(f"      [AirLabs API]: Fetching live arrivals for {airport_code} (Cache Miss)...")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"      [AirLabs API]: Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            flights_list = data.get("response")
            
            # Defensive Check: Ensure the response is actually a valid list structure
            if not isinstance(flights_list, list):
                print("      [AirLabs API Warning]: Response payload 'response' key is not a list.")
                return None
                
            live_count = len(flights_list)
            print(f"      [AirLabs API]: Success! Found {live_count} real-time active flights.")
            
            daily_estimate = max(live_count * 4, 15)
            return daily_estimate
        else:
            print(f"      [AirLabs API Warning]: Received non-200 status code from enterprise server.")
            
    except Exception as e:
        print(f"      [AirLabs API Error]: Request failed. Details: {str(e)}")
        
    return None


def generate_deterministic_airport_data(airport_code: str) -> dict:
    """
    Generates consistent infrastructure data for ANY US airport using a hybrid
    External Profile Configuration, Dynamic Inference, and Sanity-Checked Data pipeline.
    """
    airport_code = airport_code.upper().strip()
    
    # Generate static local seed for consistent fallbacks and bounding limits
    seed_number = int(hashlib.md5(airport_code.encode('utf-8')).hexdigest(), 16) % 1000000
    rng = random.Random(seed_number)
    
    # Ingest dynamic real-time traffic parameter
    live_flights = fetch_live_flights_from_api(airport_code)
    
    # --- PHASE 1: TIER & CAPACITY DETERMINATION ---
    if airport_code in AIRPORT_PROFILES:
        profile = AIRPORT_PROFILES[airport_code]
        tier = profile["tier"]
        max_capacity = profile["base_capacity"] + rng.randint(-30, 30)
        long_haul_bounds = profile["long_haul_range"]
        
        # OPERATIONAL SANITY CHECK: Detect off-peak anomalies or empty API responses
        if live_flights is not None:
            # If a Mega Hub returns less than 150 flights, it's a data outlier (e.g., midnight run)
            if tier == "Mega Hub" and live_flights < 150:
                print(f"      [Sanity Check]: Live flight count ({live_flights}) unreasonably low for a Mega Hub. Forcing fallback layer...")
                live_flights = None
            elif tier == "Large Regional" and live_flights < 60:
                print(f"      [Sanity Check]: Live flight count ({live_flights}) unreasonably low for a Large Regional. Forcing fallback layer...")
                live_flights = None

        # Stable seed-based fallback if API is dead OR if the sanity check failed
        if live_flights is None:
            if tier == "Mega Hub":
                live_flights = max_capacity + rng.randint(-100, 100)
            else:
                live_flights = max_capacity + rng.randint(-50, 50)
    
    # DYNAMIC INFERENCE LAYER: For airports outside the JSON registry
    else:
        print(f"      [Inference Engine]: Airport '{airport_code}' not found in JSON config. Deriving profile dynamically...")
        
        if live_flights is not None and live_flights >= 50:  # Require at least 50 flights for dynamic classification
            if live_flights >= 850:
                tier = "Mega Hub"
                max_capacity = rng.randint(900, 1100)
                long_haul_bounds = (8.0, 15.0)
            elif 400 <= live_flights < 850:
                tier = "Large Regional"
                max_capacity = rng.randint(550, 750)
                long_haul_bounds = (6.0, 14.0)
            else:
                tier = "Medium/Small Regional"
                max_capacity = rng.randint(180, 320)
                long_haul_bounds = (3.0, 8.0)
        else:
            # Fallback extrapolation if API is completely dead or flight count is too low to infer anything safely
            if live_flights is not None:
                print(f"      [Sanity Check]: Live count ({live_flights}) too low for reliable classification. Extrapolating...")
            else:
                print("      [Inference Warning]: API offline for unlisted asset. Extrapolating via hash seeds...")
                
            tier_selector = rng.randint(1, 3)
            if tier_selector == 1:
                tier = "Mega Hub"
                max_capacity = rng.randint(900, 1100)
                live_flights = rng.randint(850, 1200)
                long_haul_bounds = (8.0, 15.0)
            elif tier_selector == 2:
                tier = "Large Regional"
                max_capacity = rng.randint(550, 750)
                live_flights = rng.randint(450, 720)
                long_haul_bounds = (6.0, 14.0)
            else:
                tier = "Medium/Small Regional"
                max_capacity = rng.randint(180, 320)
                live_flights = rng.randint(120, 290)
                long_haul_bounds = (3.0, 8.0)

    # --- PHASE 2: METRICS MATHEMATICAL NORMALIZATION ---
    long_haul_pct = round(rng.uniform(long_haul_bounds[0], long_haul_bounds[1]), 1)
    congestion_ratio = round(live_flights / max_capacity, 2)
    
    if congestion_ratio > 1.0:
        unmet_demand_pct = round((congestion_ratio - 1.0) * 100, 1)
        unmet_reason = f"Terminal is operating at {int(congestion_ratio * 100)}% capacity. High congestion causes delays and limits airlines from adding new slots."
    else:
        unmet_demand_pct = 0.0
        unmet_reason = "Airport is operating below maximum capacity. Current infrastructure is sufficient for current demand."
        
    # --- PHASE 3: WEIGHTED INVESTMENT SCORING ALGORITHM ---
    congestion_component = min(congestion_ratio * 40, 40)
    unmet_component = min((unmet_demand_pct / 30) * 40, 40)
    long_haul_component = min((long_haul_pct / 35) * 20, 20)
    
    investment_score = round(congestion_component + unmet_component + long_haul_component, 1)
    
    return {
        "airport_code": airport_code,
        "tier": tier,
        "live_flights_daily": live_flights,
        "max_capacity_daily": max_capacity,
        "congestion_rate": congestion_ratio,
        "long_haul_flights_pct": long_haul_pct,
        "unmet_demand_pct": unmet_demand_pct,
        "unmet_demand_reason": unmet_reason,
        "investment_score": investment_score
    }

def get_airport_metrics(airport_code: str) -> dict:
    return generate_deterministic_airport_data(airport_code)