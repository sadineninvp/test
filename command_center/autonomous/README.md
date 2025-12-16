# Autonomous Agent Layer - Phase 5

LangGraph-based autonomous agent for complex multi-step tasks.

## Architecture

The autonomous agent uses LangGraph to create a stateful, graph-based workflow:

```
Ingress → Router → Planner → Agent → Tools → Verify → HIL → Summarize
```

## Components

### Graph Nodes
- **ingress**: Policy guard and state initialization
- **router**: Intent classification and routing
- **planner**: Multi-step plan creation
- **agent**: ReAct loop for tool calling
- **code_tools**: Code-related tool execution
- **web_tools**: Web-related tool execution
- **action_tools**: Action-related tool execution
- **verify**: Verification and quality checks
- **summarize**: Final summary generation
- **hil**: Human-in-the-loop approval

### Tools
All existing Action Agent tools are wrapped as LangChain tools:
- Code: read_file, write_file, list_files
- Web: web_search, fetch_url
- Action: run_command, check_service, etc.

## Usage

### Via API

```bash
# Use autonomous agent
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"request": "add authentication to the project", "autonomous": true}'
```

### Via CLI

```bash
# Use autonomous mode (when CLI updated)
python3 iqide.py "add authentication" --autonomous
```

## State Persistence

State is persisted using SQLite checkpointer:
- Location: `storage/checkpoints/agent_state.db`
- Enables conversation resumption
- Tracks execution state

## Human-in-the-Loop

Dangerous operations require approval:
- File deletion
- System configuration changes
- Service operations
- Large-scale changes

Approve via API:
```bash
curl -X POST http://localhost:8000/api/approve \
  -H "Content-Type: application/json" \
  -d '{"approval_id": "...", "approved": true}'
```

## Dependencies

See `requirements.txt` for LangGraph dependencies.

