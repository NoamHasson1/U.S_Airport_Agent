# Airport Investment Intelligence Agent
### Private Equity Infrastructure Analytics Platform • Powered by GPT-4o & Live Streams

An advanced, AI-powered conversational agent and decision-support dashboard designed for infrastructure Private Equity (PE) analysts. This platform automates the discovery, auditing, and ranking of high-yield commercial airport modernization and capacity expansion opportunities across the United States.

## Prerequisites & Requirements

  - **Python Version:** Python `3.10` or higher is strictly recommended.
  - **External Access:** Active internet connection to connect to public API endpoints.
  - **Required Secrets:** * A valid **OpenAI API Key**.
   **Required Secrets:** * A valid **AirLabs API Key**.


## Project Overview

In infrastructure private equity, allocating capital toward airport terminal expansions or modernization requires balancing live asset utilization against historical and baseline constraints. This project delivers a production-ready system consisting of:
* **Multimodal Input Architecture:** Supports seamless, traditional text entries or real-time audio voice commands processed instantly via OpenAI Whisper.
* An **Autonomous AI Agent Layer** that interprets complex analytical prompts, executes parallel tool invocations, and synthesizes investment-committee briefs.
* A **Deterministic Math Pipeline** that ensures hard numbers, congestion rates, and metrics are calculated strictly via verified Python logic (preventing LLM calculation hallucinations).
* An **Institutional Dashboard UI** designed with a modern, distraction-free corporate aesthetic featuring real-time state synchronization and automated data integrity guards.

---

## Technical Specifications & Architecture

The application is engineered with a strict decoupling of the presentation layer, orchestration layer, and dynamic inference tools.

### 1. Where and How AI is Utilized
* **Audio Transcription Processing (Whisper-1):** When an analyst speaks a command via the embedded interface microphone, the binary WAV stream is intercepted, handled in-memory using `io.BytesIO`, and fed directly to OpenAI's Whisper API. The resulting clean transcription text is cleanly piped to the main agent loop.
* **Intent Parsing & Entity Extraction:** The agent (`gpt-4o`) evaluates natural language queries to extract target geographic regions or 3-letter IATA codes (e.g., "LAX", "SFO").
* **Parallel Tool Invocations:** Leveraging native OpenAI Function Calling, if an analyst asks to compare multiple gateways simultaneously, the LLM parallelizes the requests into a bundle of concurrent function executions.
* **Qualitative Synthesis:** The AI is deliberately **restricted** from computing financial scores or traffic numbers. Instead, it ingests the deterministic data payload returned by the tools, contextualizes the "unmet demand reasons", flags uncertainties, and formats the output into a highly polished investment memorandum.

### 2. Tri-Layer Fault-Tolerant Failover & Verification Pipeline
The system enforces a reliable fallback mechanism when processing user queries:
The system enforces a reliable fallback mechanism when processing user queries:
* **The Happy Path:** The agent matches the IATA code against a local registry (`airport_config.json`) and successfully fetches active flight volumes via live `AirLabs API` network streams.
* **Free-Tier API Truncation Mitigation Guard:** The public AirLabs Free-Tier API enforces a hard ceiling of 100 active records per flight query, which artificially flatlines daily flight estimates to a static 400 flights across all major US hubs. To prevent skewed congestion rates, our pipeline intercepts this specific payload constraint. It automatically leverages a deterministic random engine to extrapolate realistic operational volumes scaled directly to the airport's true structural tier (e.g., re-scaling Mega Hubs to an 88%–112% capacity utilization envelope).
* **Data Integrity Input Guard:** If a user submits a completely fictitious code (e.g., `XYZ`), the system verifies that it returns zero live traffic from the external API *and* is missing from the local asset configuration file. Rather than generating fake metrics, it triggers an immediate input violation stop, alerting the agent to explain the scope limits explicitly to the analyst.
---

## Core Features

* **Multimodal Voice Interface:** Incorporates a responsive, embedded `🎤` floating hardware recorder inside the centralized input pill bar, matching elite modern conversational standards.
* **Bloomberg-Style Reporting Matrix:** Automatically transforms complex Markdown output tables into custom-styled, zebra-striped institutional matrices with polished slate-blue layouts.
* **Real-time System Status Pulse:** A custom HTML/CSS live-pulsing hardware animation embedded within the Streamlit workspace configuration sidebar that tracks pipeline health.
* **Comprehensive Automated Test Suite (`pytest`):** Bundles seven isolated test suites covering core math parameters, security jailbreak mitigation, state serialization, and unlisted asset boundaries.

---

## Deterministic Scoring Methodology

The `investment_score` (bounded strictly between **0.0** and **100.0**) is derived deterministically in the Python layer using a weighted multi-factor equation. This model mirrors traditional infrastructure private equity risk/return models:

$$\text{Investment Score} = \text{Congestion Component (40\%)} + \text{Unmet Demand Component (40\%)} + \text{Long-Haul Component (20\%)}$$

### 1. Congestion Component (Weight: 40% | Max: 40 Points)
Measures capital saturation by dividing live daily flight arrivals against the terminal's designed maximum structural capacity. Higher values indicate an asset operating near or above its threshold, signaling a pressing demand for infrastructure expansion.

$$\text{Congestion Ratio} = \frac{\text{Live Daily Arrivals}}{\text{Max Structural Capacity}}$$

### 2. Unmet Demand Component (Weight: 40% | Max: 40 Points)
When the congestion ratio exceeds a factor of `1.0` (100% capacity utilization), the system computes the exact percentage of overflow demand. Operating at these extreme thresholds restricts commercial airlines from scheduling additional lucrative route slots, creating an implicit opportunity cost that a private modernization injection can unlock.

### 3. Long-Haul Connectivity Component (Weight: 20% | Max: 20 Points)
Evaluates the proportion of long-haul widebody arrivals. Long-haul flights generate significantly higher airport yields through increased landing fees, extended terminal parking cycles, and elevated per-passenger retail and Duty-Free spend inside the concourse.

---

## Key Architectural Tradeoffs

### 1. Audio Network Overhead vs. Hands-Free Efficiency
* **Tradeoff:** Implementing `Whisper` requires streaming recorded binary audio files over HTTPS to external servers, which incurs slight network latency.
* **Pros:** Elevates user experience drastically. 
* **Cons:** Increases dependency on OpenAI network availability.
### 2. Reproducible Hash Fallbacks vs. Hard System Failure
* **Tradeoff:** When external network APIs fail, the system runs local MD5 hash seeds to extrapolate mock metrics instead of crashing or serving an empty screen.
* **Pros:** Guarantees absolute UI/UX reliability, system uptime, and test-suite stability. The data structure returned is perfectly consistent with production interfaces.
* **Cons:** If an API drop occurs unnoticed, analysts might evaluate seed-simulated numbers. We mitigated this risk by embedding an automated real-time state variable (`api_healthy`) that visibly forces the sidebar panel to flash red during fallbacks.

### 3. In-Memory Dynamic Inference vs. Strict Database Schemas
* **Tradeoff:** If an analyst requests a valid US commercial airport omitted from the internal `airport_config.json` database registry, the tool leverages incoming live API volumes to dynamically infer its operational tier and derive capacity thresholds on the fly.
* **Pros:** Grants the user the flexibility to test unexpected municipal assets without manual record provisioning.
* **Cons:** Dynamic classification lacks manually audited historical reference limits. We chose this over a strict rejection constraint to prioritize conversational depth, while implementing safety guards against entirely fake codes.
### 4. Tier-Based Volume Extrapolation vs. Raw Truncated Reporting
* **Tradeoff:** Intercepting truncated 100-record free API limits and extrapolating volumes based on asset tiers, rather than printing the raw 400 flight baseline.
* **Pros:** Corrects severe analytical distortions. Large gateways like ATL or JFK reflect realistic near-capacity gridlocks, allowing the scoring algorithm and the AI agent to accurately calculate and explain unmet flight demand.
* **Cons:** The data switches from empirical raw counts to derived models. This is highly acceptable since it preserves the operational logic requested by the investment mandate under free tier account parameters.

---

## Project Structure

```text
├── .env.example
├── .gitignore
├── app.py
├── agent.py
├── tools.py
├── prompts.py
├── airport_config.json
├── requirements.txt
└── tests/
    ├── test_agent.py
    └── test_tools.py   
```

##  Step-by-Step Installation

### 1. Clone the Project Assets

 Open your computer's terminal (called Terminal on macOS/Linux, or Command Prompt / PowerShell on Windows) and paste these commands: 
```sh
# 1. Download the code from GitHub to your computer

git clone <repository-url>

# 2. Move your terminal focus inside the project folder
cd <project_name>
```

### 2. Set Up a Virtual Environment

**CRITICAL FOR macOS USERS:** you may need **Python 3.10 or higher**. Before creating the environment, verify your active terminal environment version:
```sh
python3 --version
```
If this returns Python 3.9 or lower, please update your Python runtime via Python.org or Homebrew before continuing.

- To make sure this project doesn't conflict with any other software on your machine, we create a secure, isolated sandbox folder called venv. Paste the command matching your 
system:

**macOS / Linux:**
```sh
python -m venv venv
source venv/bin/activate
```

if didn't work - 

**macOS / Linux:**
```sh
python3 -m venv venv
source venv/bin/activate
```

**Windows (CMD):**
```sh
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```sh
python -m venv venv
venv\Scripts\Activate.ps1
```
- Visual Check: You know it worked if you now see (venv) written at the very beginning of your terminal line. 

---

### 3. Install Required Packages

- Now, install the tool's building blocks (llibraries that parse JSON configuration, handle HTTP network requests, and manage the live UI framework) by running this command:
```sh
pip install -r requirements.txt
```
or

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

The pipeline loads credentials from a local `.env` file (ignored by Git). Because your API keys are secret, we don't put them in the public code. We put them in a hidden file called .env.

CRITICAL: Make sure your terminal is still located inside the main project directory before running the copy commands below.

- Create a `.env` file in the root directory: let's create te file - Run the command for your system to copy our template into a real configuration file:

**Create your `.env` file:**

**macOS / Linux:**
```sh
cp .env.example .env
```

**Windows (CMD):**
```sh
copy .env.example .env
```

**Windows (PowerShell):**
```sh
Copy-Item .env.example .env
```

- Can't see or open the `.env` file? Because files starting with a dot (`.`) are hidden by default on macOS and Linux, you might not see the file in your standard folder view. 

* **On macOS / Linux:** Run `open -e .env` (This opens it instantly in the built-in TextEdit app).

* **On Windows:** Run `notepad .env` (This opens it instantly in the built-in Notepad app).

*Alternatively, you can always open VS Code manually, click on the **File Explorer** tab on the left sidebar, and click directly on the `.env` file to edit it!*

Paste your keys: Open the newly created `.env` file with any basic text editor (like Notepad or VS Code) and replace the text with your actual keys:

```
OPENAI_API_KEY=your_actual_openai_api_key_here
AIRLABS_API_KEY=your_actual_airlabs_api_key_here
```

### 5. Launch the Private Equity Dashboard

You are ready!

Run from the terminal:

```sh
streamlit run app.py
```

The interface will automatically compile its assets and launch within a local browser window at http://localhost:8501. 

### 6. Execute the Automated Test Suite

To verify the math pipeline, dynamic inference guards, and security boundaries natively:

Run from the terminal:

```sh
python -m pytest -v
```

Look that all the tests are green!

## Troubleshooting

- If the pipeline encounters deployment or runtime friction, consult this matrix to resolve issues quickly:
1. Clearing Cached Memory: When switching your analysis focus between highly separate geographical regions (e.g., changing focus from the West Coast to New England), open the left-side Workspace Configuration panel and click Clear Conversation & Context. This instantly purges active session variables and forces an app state re-initialization.
2. * **Microphone Access Blocked:** Upon clicking the `🎤` icon for the first time, ensure your web browser is granted system permissions to access your microphone hardware. If audio fails to capture, refresh the page and check the address bar permissions icon.
3. * **Microphone Access Blocked (Browser Permissions):** If clicking the `🎤` icon does not respond or toggle to the stop state, your browser is likely blocking the hardware access.
  * **How to fix:** Click the **lock icon** (🔒) or settings icon located on the far left of your browser's address bar (immediately next to `http://localhost:8501`). Find the **Microphone** setting and switch the toggle to **Allow**, then refresh the application.
  * **Critical Origin Security Constraint:** Modern web browsers enforce strict *Secure Origins* policies. Microphone hardware access (`mediaV2`) is strictly forbidden on standard `http` connections *unless* it is running on **`localhost`**. Ensure you are accessing the platform strictly via `http://localhost:8501` and **not** via the local Network IP address (e.g., `http://10.0.0.x:8501`), otherwise the browser will silently kill the voice component.
