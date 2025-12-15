# IQIDE - Intelligent Query IDE

Multi-phase implementation of a Computer Action Agent system with Command Center orchestration.

## Current Status: Phase 4 Complete 

### Phase 1: Computer Action Agent 
Execution layer for system operations - a tool library that:
- Executes shell commands safely
- Manages system services (start, stop, restart, check)
- Logs all actions for audit purposes
- Handles errors gracefully
- Returns structured results

**Important**: This is NOT an AI agent. It's just Python functions that execute commands.

### Phase 2: Command Center (Hardcoded) 
Routing and orchestration layer with hardcoded logic (no LLM):
- Parses user requests using pattern matching
- Routes to action plans (hardcoded mappings)
- Orchestrates multi-step workflows
- Formats results for users
- Provides HTTP API via FastAPI

**Note**: Phase 2 is still available for testing without LLM costs.

### Phase 3: Command Center (LLM-Powered) 
AI-powered routing using OpenAI function calling:
- Uses LLM to understand natural language requests
- LLM decides which Action Agent functions to call
- Supports conversational, flexible requests
- Intelligent multi-step planning
- Same HTTP API with `use_llm=true` parameter

**Requirements**: OpenAI API key (set `OPENAI_API_KEY` environment variable)

### Phase 4: Local Client (CLI) 
Command-line interface for end users:
- Connects to Command Center API
- Supports both Phase 2 and Phase 3 modes
- Configuration management
- Pretty result formatting
- Health checks and utilities

**Features:**
- CLI interface (`iqide.py`)
- Configuration file (`~/.iqide/config.json`)
- Error handling and connection checks
- JSON or pretty output formats

## Quick Start

### Install

```bash
cd iqide
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Test Phase 1 (Action Agent)

```bash
python test_action_agent.py
```

### Test Phase 2 (Command Center - Hardcoded)

```bash
python test_command_center.py
```

### Test Phase 3 (Command Center - LLM)

**First, set your OpenAI API key:**
```bash
export OPENAI_API_KEY="your-key-here"
```

Then run:
```bash
python3 test_llm_command_center.py
```

### Test Phase 4 (Local Client)

**First, start the Command Center server:**
```bash
uvicorn command_center.api:app --reload
```

**Then in another terminal, use the CLI:**
```bash
# Install dependencies first
pip install -r requirements.txt

# Use the client (single commands)
python3 iqide.py "what is my username?"
python3 iqide.py "run ls -la" --no-llm
python3 iqide.py "restart nginx" --llm

# Check server health
python3 iqide.py --health-check

# Interactive session (for testing with state persistence)
python3 interactive_test.py
```

**Interactive Session:**
The interactive session maintains state across requests, so directory changes and other state persists:
```bash
python3 interactive_test.py

iqide> what is the current directory?
iqide> go to /Users
iqide> what directory are you in?  # Will show /Users!
iqide> exit
```

### Run API Server

```bash
uvicorn command_center.api:app --reload
```

**Test Phase 2 (hardcoded):**
```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"request": "run whoami", "use_llm": false}'
```

**Test Phase 3 (LLM):**
```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"request": "what is my username?", "use_llm": true}'
```

### Use in Your Code

#### Phase 1: Direct Action Agent Usage

```python
from action_agent import CommandExecutor, ServiceManager

# Command execution
executor = CommandExecutor()
result = executor.run("ls -la")
print(result["output"])

# Service management
service_mgr = ServiceManager()
status = service_mgr.check_service("nginx")
print(status)
```

#### Phase 2: Command Center Usage (Hardcoded)

```python
from command_center import CommandCenter

# Create Command Center (hardcoded routing)
center = CommandCenter()

# Handle requests (must match patterns)
result = center.handle("run whoami")
print(result["message"])

result = center.handle("check nginx")
print(result["message"])
```

#### Phase 3: Command Center Usage (LLM-Powered)

```python
import os
from command_center import LLMCommandCenter

# Set API key
os.environ["OPENAI_API_KEY"] = "your-key"

# Create LLM-powered Command Center
center = LLMCommandCenter()

# Handle natural language requests (flexible!)
result = center.handle("what is my username?")
print(result["message"])

result = center.handle("list files in current directory")
print(result["message"])

result = center.handle("tell me about my system")
print(result["message"])
```

#### Phase 4: CLI Client Usage

```bash
# Basic usage
python3 iqide.py "what is my username?"

# Use Phase 2 (hardcoded)
python3 iqide.py "run whoami" --no-llm

# Use Phase 3 (LLM)
python3 iqide.py "what files are in the current directory?" --llm

# Check server health
python3 iqide.py --health-check

# Configuration
python3 iqide.py --config-get api_url
python3 iqide.py --config-set default_use_llm true

# List available actions/tools
python3 iqide.py --list-actions  # Phase 2
python3 iqide.py --list-tools    # Phase 3

# JSON output
python3 iqide.py "run ls" --json
```

## Project Structure

```
iqide/
 action_agent/                    # Phase 1: Execution Layer
    __init__.py
    command_executor.py          # Command execution
    service_manager.py           # Service management
    logger.py                    # Audit logging
    config.py                    # Configuration
 client/                          # Phase 4: Local Client
    __init__.py
    api_client.py               # HTTP client for Command Center
    config.py                   # Configuration management
    formatter.py                # Result formatting
    cli.py                      # CLI interface
 command_center/                  # Phase 2 & 3: Routing Layer
    __init__.py
    command_center.py            # Phase 2: Hardcoded routing
    llm_command_center.py        # Phase 3: LLM-powered routing
    llm_client.py                # Phase 3: OpenAI integration
    tool_definitions.py          # Phase 3: Tool definitions for LLM
    function_caller.py           # Phase 3: Execute LLM function calls
    request_parser.py            # Phase 2: Parse user requests
    action_router.py             # Phase 2: Route to action plans
    orchestrator.py              # Phase 2: Execute plans
    formatter.py                 # Format results
    api.py                       # FastAPI server (both phases)
 logs/                            # Generated logs
    action_agent.log
    action_agent.db
 iqide.py                         # Phase 4: CLI entry point
    test_action_agent.py             # Phase 1 tests
    test_command_center.py           # Phase 2 tests
    test_llm_command_center.py       # Phase 3 tests
    test_client.py                   # Phase 4 tests
    requirements.txt                 # Dependencies
    README.md                        # This file
```

## Features

### Phase 1: Action Agent 
-  Command execution with timeout and error handling
-  Service management (check, start, stop, restart)
-  Audit logging (file + SQLite database)
-  Cross-platform support (Linux, macOS, Windows)

### Phase 2: Command Center (Hardcoded) 
-  Request parsing (pattern matching)
-  Action routing (hardcoded mappings)
-  Multi-step orchestration
-  Result formatting
-  HTTP API (FastAPI)
-  Supported actions: restart_service, start_service, stop_service, check_service, run_command, list_services

### Phase 3: Command Center (LLM-Powered) 
-  OpenAI function calling integration
-  Natural language understanding
-  Intelligent tool selection by LLM
-  Multi-step planning and execution
-  Conversational requests
-  Same HTTP API with `use_llm=true` parameter

### Phase 4: Local Client (CLI) 
-  Command-line interface
-  HTTP client for Command Center API
-  Configuration file management (`~/.iqide/config.json`)
-  Pretty and JSON output formats
-  Health check utility
-  Supports both Phase 2 and Phase 3 modes

## Supported Request Patterns

The Command Center (Phase 2) supports these patterns:

- **Service Management:**
  - `restart <service>` / `reboot <service>`
  - `start <service>` / `start the <service>`
  - `stop <service>` / `stop the <service>`
  - `check <service>` / `status <service>` / `<service> status`

- **Commands:**
  - `run <command>` / `execute <command>`
  - `run command <command>`

- **Service Lists:**
  - `list services` / `show services`

## Next Steps

-  Phase 1: Computer Action Agent
-  Phase 2: Command Center (hardcoded routing)
-  Phase 3: Command Center (LLM-powered)
-  Phase 4: Local Client (CLI)
-  Future: Desktop GUI or IDE Extension (optional)

## Using Phase 2 vs Phase 3

**Phase 2 (Hardcoded):**
-  No API costs
-  Fast and predictable
-  Works offline
-  Limited to predefined patterns
-  Less flexible

**Phase 3 (LLM-Powered):**
-  Understands natural language
-  Very flexible requests
-  Intelligent planning
-  Requires OpenAI API key
-  Has API costs
-  Slightly slower

**Recommendation**: Use Phase 2 for testing and simple workflows. Use Phase 3 for production and complex, flexible requests.

## Quick Start Guide

### 1. Install Dependencies
```bash
cd iqide
pip install -r requirements.txt
```

### 2. Start Command Center Server
```bash
# Terminal 1
uvicorn command_center.api:app --reload
```

### 3. Use the CLI Client
```bash
# Terminal 2
# Phase 2 (hardcoded, no API key needed)
python3 iqide.py "run whoami" --no-llm

# Phase 3 (LLM, requires API key)
export OPENAI_API_KEY="sk-your-key"
python3 iqide.py "what is my username?" --llm
```

### Configuration
The client stores configuration in `~/.iqide/config.json`:
- `api_url`: Command Center API URL (default: http://localhost:8000)
- `default_use_llm`: Default to use LLM mode (default: false)
- `timeout`: Request timeout in seconds (default: 30)
- `output_format`: Output format - "pretty" or "json" (default: "pretty")

View/edit config:
```bash
python3 iqide.py --config-get api_url
python3 iqide.py --config-set default_use_llm true
```

## Security Note

 **Development Phase**: Currently no command restrictions. Add security restrictions before production use.
