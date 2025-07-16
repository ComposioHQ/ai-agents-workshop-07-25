# Simple Python Calculator

A command-line calculator with basic operations (add, subtract, multiply, divide).
## Usage

```
python main.py <operation> <a> <b>
```

- `<operation>`: `add`, `sub`, `mul`, or `div`
- `<a>` and `<b>`: numeric (float/int) operands

### Examples

Addition:
```
python main.py add 2 5
# Result: 7.0
```

Division by zero:
```
python main.py div 7 0
# Error: Division by zero
```

## Files
- `main.py`: CLI interface
- `operations.py`: Calculator functions

# Multi-Agent Software Development System with State Management

This module builds upon the previous multi-agent system by adding sophisticated state management capabilities. The system now remembers conversations across runs, tracks file creation to prevent duplicates, and maintains a simple memory layer for project context.

## New Features

### 1. 🧠 Conversation Memory with OpenAI Agents SDK Sessions

The system now uses OpenAI Agents SDK Sessions to automatically maintain conversation history across multiple runs:

```python
# Create session for conversation memory
session = SQLiteSession(session_id)

# Run agent with session - it automatically remembers previous conversations
result = await Runner.run(
    starting_agent=triage_agent,
    input=user_request,
    context=context,
    session=session,  # This enables conversation memory across runs
    run_config=run_config,
    hooks=hooks,
    max_turns=50
)
```

**Benefits:**
- Agents remember previous user queries and responses
- Context is maintained across multiple agent runs
- No need to manually manage conversation history
- Each session has its own separate conversation thread

### 2. 📁 File Tracking Hooks

A simple hook system tracks when files are created to prevent duplicates:

```python
class StateManagementHooks(RunHooks):
    async def on_tool_call_end(self, context: RunContextWrapper, tool_call, result) -> None:
        """Track file creation to prevent duplicates"""
        if hasattr(tool_call, 'function') and tool_call.function.name == 'filetool_create_file':
            # Parse filename and track it
            filename = args.get('file_path', '')
            if filename and filename not in self.context.files_created:
                self.context.files_created.append(filename)
                # Update persistent memory
                memory = self.context.load_memory()
                memory["files_created"].append(filename)
                self.context.save_memory(memory)
```

**Benefits:**
- Prevents agents from recreating files that already exist
- Tracks files both in current session and across sessions
- Simple hook-based implementation that's easy to understand

### 3. 💾 Simple Memory Layer

A JSON-based memory system that persists project information:

```python
@dataclass
class ProjectContext:
    def save_memory(self, data: Dict[str, Any]):
        """Save data to memory file"""
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_memory(self) -> Dict[str, Any]:
        """Load data from memory file"""
        # Returns: {"conversations": [], "files_created": [], "project_summary": ""}
    
    def add_conversation_summary(self, summary: str):
        """Add conversation summary to memory"""
        memory = self.load_memory()
        memory["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        })
        self.save_memory(memory)
```

**Benefits:**
- Persists project state between sessions
- Stores conversation summaries for future reference
- Tracks all files created across sessions
- Simple JSON format that's human-readable

### 4. 🔧 New Agent Tools

The system provides new tools for agents to interact with the state management system:

#### `check_file_exists(filename: str) -> str`
```python
@function_tool
def check_file_exists(context: RunContextWrapper[ProjectContext], filename: str) -> str:
    """Check if a file was already created to prevent duplicates"""
    if filename in context.context.files_created:
        return f"File {filename} already exists in this session"
    
    memory = context.context.load_memory()
    if filename in memory["files_created"]:
        return f"File {filename} was created in a previous session"
    
    return f"File {filename} does not exist yet"
```

#### `get_project_memory() -> str`
```python
@function_tool
def get_project_memory(context: RunContextWrapper[ProjectContext]) -> str:
    """Get project memory including past conversations and files"""
    memory = context.context.load_memory()
    
    summary = f"Project: {context.context.project_name}\n"
    summary += f"Project Summary: {memory.get('project_summary', 'No summary yet')}\n\n"
    
    if memory["files_created"]:
        summary += f"Files Created: {', '.join(memory['files_created'])}\n\n"
    
    if memory["conversations"]:
        summary += "Recent Conversations:\n"
        for conv in memory["conversations"][-3:]:  # Show last 3 conversations
            summary += f"- {conv['timestamp']}: {conv['summary']}\n"
    
    return summary
```

#### `summarize_session(summary: str) -> str`
```python
@function_tool
def summarize_session(context: RunContextWrapper[ProjectContext], summary: str) -> str:
    """Summarize the current session for future reference"""
    context.context.add_conversation_summary(summary)
    return f"Session summary saved: {summary}"
```

## Usage Examples

### Basic Usage with State Management

```python
# Run the system with state management
result = await run_multi_agent_system_with_state(
    user_request="Create a Python calculator with basic operations",
    project_name="CalculatorProject",
    session_id="user_123"
)

# Run again in the same session - it will remember the previous context
result2 = await run_multi_agent_system_with_state(
    user_request="Add a square root function to the calculator",
    project_name="CalculatorProject", 
    session_id="user_123"  # Same session ID
)
```

### Agent Instructions Enhanced with State Management

All agents now have enhanced instructions that include state management:

```python
"""
IMPORTANT STATE MANAGEMENT:
- Always check project memory first to understand what has been done before
- Use check_file_exists before creating files to avoid duplicates
- Build upon existing files rather than recreating them
- Summarize your session before handing off
"""
```

## Demo Script

The module includes a comprehensive demo that shows:

1. **First Request**: Creates initial files for a calculator project
2. **Second Request**: Adds functionality while remembering previous context
3. **Third Request**: Creates tests while avoiding file duplication

```python
async def demo_state_management():
    session_id = "demo_session"
    
    # First request - creates some files
    request1 = """
    Create a simple Python calculator that:
    1. Has functions for basic operations (+, -, *, /)
    2. Includes error handling for division by zero
    3. Has a simple CLI interface
    """
    result1 = await run_multi_agent_system_with_state(request1, "CalculatorProject", session_id)
    
    # Second request - should remember the previous conversation
    request2 = """
    Now add a function to calculate the square root and modify the CLI to support it.
    """
    result2 = await run_multi_agent_system_with_state(request2, "CalculatorProject", session_id)
    
    # Third request - should avoid recreating files
    request3 = """
    Create comprehensive unit tests for the calculator functions.
    """
    result3 = await run_multi_agent_system_with_state(request3, "CalculatorProject", session_id)
```

## Key Benefits

### 1. **Conversation Continuity**
- Agents remember what was said before
- No need to repeat context in follow-up requests
- Natural conversation flow across multiple runs

### 2. **File Management**
- Prevents duplicate file creation
- Agents know what files exist from previous sessions
- Efficient resource utilization

### 3. **Project Context**
- Maintains project state across sessions
- Conversation summaries for future reference
- Easy to understand what has been done before

### 4. **Educational Value**
- Simple, bare-minimum implementation
- Easy to understand and modify
- Demonstrates core concepts without over-engineering

## Technical Details

### Memory Storage
- Uses JSON files for persistence (`memory_{session_id}.json`)
- Each session has its own memory file
- Human-readable format for debugging

### Session Management
- Uses OpenAI Agents SDK `SQLiteSession` for conversation memory
- Automatic conversation history management
- Separate sessions for different users/projects

### Hook System
- Extends the existing `RunHooks` class
- Simple `on_tool_call_end` hook for file tracking
- Minimal implementation that's easy to understand

## Installation & Setup

1. Install dependencies:
```bash
pip install agents composio-openai-agents python-dotenv
```

2. Set up environment variables:
```bash
OPENAI_API_KEY=your_api_key_here
```

3. Run the demo:
```bash
python state_multi_agent_system.py
```

## File Structure

```
4-state-management/
├── state_multi_agent_system.py  # Main system with state management
├── README.md                    # This file
├── memory_demo_session.json     # Example memory file (created at runtime)
└── .composio.lock              # Composio configuration
```

## Next Steps

This implementation provides a solid foundation for state management in multi-agent systems. You can extend it by:

1. Adding more sophisticated memory types (vector databases, embeddings)
2. Implementing memory search and retrieval
3. Adding memory expiration and cleanup
4. Creating more advanced summarization techniques
5. Adding memory sharing between different projects

The current implementation is intentionally kept simple to demonstrate the core concepts and mechanisms that make state management work in multi-agent systems. 