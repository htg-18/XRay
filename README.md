# X-Ray: Debugging Library for Multi-Step Algorithmic Systems

A Python library for capturing execution traces, evaluations, and reasoning from complex multi-step processes. Includes a web-based dashboard for visualization.

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone or download this repository

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python api_server.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

### Storage Modes

The application automatically detects the deployment environment:

- **Local Mode**: Saves execution traces and evaluations to local `xray_data/` directory
- **Vercel Mode**: Uses Vercel Blob Storage API for persistent cloud storage

This allows the same codebase to work seamlessly in both local development and production deployment.

## Usage

The dashboard provides two main features:

1. **Run Demo**: Execute a sample competitor product selection pipeline with customizable parameters

The demo simulates a product selection system that:
- Generates search keywords using LLM
- Searches for candidate products
- Applies filters (price, rating, reviews)
- Removes false positives with LLM
- Ranks and selects the best competitor

## Approach

### Core Library Design

The X-Ray library uses context managers to automatically track execution flow. Each execution contains multiple steps, and each step can have:
- Type classification (llm, api, filter, ranking)
- Input/output data
- Reasoning explanation
- Execution metrics (duration, status)
- Evaluation streams for large datasets

### Streaming Evaluations

For steps that process many items (e.g., filtering 50 products), evaluations are written to JSONL files instead of being stored in memory. The dashboard loads these files with pagination to handle large datasets efficiently.

### Dashboard Architecture

A Flask server serves the HTML dashboard and provides API endpoints for running demos and fetching execution data. The dashboard uses vanilla JavaScript to render execution traces with collapsible sections and paginated evaluations.

## Known Limitations and Future Improvements

**Limited Historical Execution Management**: The current implementation saves executions to disk but provides no UI for browsing historical runs. A future version would include an execution history browser with search and filtering capabilities.

**No Real-Time Execution Monitoring**: Executions are only visible after completion. For long-running processes, adding WebSocket support would enable real-time progress updates and intermediate results viewing.

**Single-User Local Deployment**: The system is designed for local development use. Production deployment would require authentication, multi-user support, persistent database storage, and proper security measures for handling execution data.

