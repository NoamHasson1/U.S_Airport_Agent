import json
import streamlit as st 
from openai import OpenAI
from tools import get_airport_metrics
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

# Configuration Constants
MODEL_NAME = "gpt-4o"

# Initialize the OpenAI client
client = OpenAI()

# Define the tool configuration with explicit long-haul capabilities description
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_airport_metrics",
            "description": "Get real-time and deterministic infrastructure, congestion, unmet demand, long-haul flight percentages, and investment scores for any US airport using its 3-letter IATA code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": "The 3-letter IATA code of the airport (e.g., 'LAX', 'SFO', 'BOS', 'SNA')."
                    }
                },
                "required": ["airport_code"]
            }
        }
    }
]

def serialize_history_to_dicts(history_list: list) -> list:
    """
    Helper function to safely transform a mix of OpenAI Pydantic objects 
    and standard dictionaries into uniform, UI-safe standard Python dicts.
    """
    clean_history = []
    for msg in history_list:
        if isinstance(msg, dict):
            clean_history.append(msg)
        elif hasattr(msg, "model_dump"):
            clean_history.append(msg.model_dump(exclude_none=True))
        elif hasattr(msg, "dict"):
            clean_history.append(msg.dict(exclude_none=True))
        else:
            clean_history.append(dict(msg))
    return clean_history

def run_investment_agent(user_message: str, chat_history: list = None) -> tuple:
    """
    Executes the conversational agent loop with persistent state tracking and parallel tool auditing.
    Returns: (str: response_text, list: updated_chat_history)
    """
    # Initialize API health state if not already set
    st.session_state.api_healthy = True

    if chat_history is None:
        chat_history = []
        
    # Build the internal conversational payload ensuring the system prompt anchors the run
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})
    
    print(f"\n[User Prompt]: '{user_message}'")
    print(f"[{MODEL_NAME}]: Analyzing prompt intent...")

    try:
        # Step 1: Fire initial intent parsing requests
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
    except Exception as e:
        error_msg = f"Inference engine failure during initialization. Details: {str(e)}"
        print(f"  [System Error]: {error_msg}")
        return f"An upstream LLM error occurred: {str(e)}", chat_history

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Update our local execution message list with the LLM's first response turn
    messages.append(response_message)
    
    # Step 2: Orchestrate Parallel Tool Execution Loop if requested
    if tool_calls:
        print(f"\n[Tool Call Detected]: {MODEL_NAME} requested {len(tool_calls)} parallel function execution(s).")
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            airport_code = function_args.get("airport_code", "").upper().strip()
            
            print(f"  ├── Calling Function: '{function_name}' for target asset: '{airport_code}'")
            
            if function_name == "get_airport_metrics":
                try:
                    # Execute python data pipeline defensively
                    tool_output = get_airport_metrics(airport_code)
                    print(f"  └── Tool Returned Payload: Score={tool_output.get('investment_score')}, Congestion={tool_output.get('congestion_rate')}, Unmet Demand={tool_output.get('unmet_demand_pct')}%")
                except Exception as tool_exc:
                    st.session_state.api_healthy = False
                    
                    # Create a graceful fallback payload so the LLM knows the tool failed instead of crashing the UI
                    print(f"  [Tool Error]: Function execution failed for {airport_code}. Details: {str(tool_exc)}")
                    tool_output = {
                        "airport_code": airport_code,
                        "error": f"Failed to retrieve operational metrics for {airport_code} due to backend execution failure."
                    }
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_output)
                })
        
        print(f"\n[{MODEL_NAME}]: Processing tool payload outputs and synthesizing final investment committee brief...")
        try:
            # Step 3: Gather final unified summary synthesis from the LLM
            final_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            print("[Done]: Response successfully generated and synchronized with UI.\n")
            
            # CRITICAL: Strip the system prompt anchor before saving back to the application state
            final_messages = messages + [final_response.choices[0].message]
            updated_history = final_messages[1:] # Excludes the first element (the system prompt)

            return final_response.choices[0].message.content, serialize_history_to_dicts(updated_history)

        except Exception as e:
            return f"Failed to synthesize tool data payload into an executive brief. Details: {str(e)}", chat_history
        
    print(f"\n[No Tool Needed]: {MODEL_NAME} bypassed tool pipeline. Direct context boundary enforced.")
    print("[Done]: Response sent to UI.\n")
    
    # If no tools were called, the history update is a simple user-assistant pairing
    updated_history = messages[1:]
    return response_message.content, serialize_history_to_dicts(updated_history)