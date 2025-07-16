#!/usr/bin/env python3
"""
Multi-Agent Software Development System with State Management

This demonstrates a production-ready multi-agent system with:
1. Specialized agents for different tasks
2. Handoff mechanisms between agents
3. Cost optimization using different models
4. Composio tool integration
5. Practical software development workflow
6. **State Management and Memory System**
"""

import os
import sys
import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# OpenAI Agents SDK imports
from agents import Agent, Runner, handoff, RunConfig, function_tool, trace, RunHooks, RunContextWrapper
# Composio imports
from composio_openai_agents import ComposioToolSet, Action, App

# Load environment variables
load_dotenv()

@dataclass
class ConversationEntry:
    """Single conversation entry with metadata"""
    timestamp: datetime
    agent_name: str
    message_type: str  # "input", "output", "handoff", "error"
    content: str
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProjectMemory:
    """Persistent project memory - like claude.md"""
    project_name: str
    created_at: datetime
    last_updated: datetime
    
    # Core project information
    original_requirements: str
    current_objectives: List[str] = field(default_factory=list)
    architecture_decisions: List[str] = field(default_factory=list)
    
    # Files and artifacts
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    key_functions: List[str] = field(default_factory=list)
    
    # Learning and patterns
    successful_patterns: List[str] = field(default_factory=list)
    failed_approaches: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    
    # Progress tracking
    milestones_completed: List[str] = field(default_factory=list)
    current_blockers: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    
    # Agent interactions
    agent_specializations: Dict[str, str] = field(default_factory=dict)
    handoff_patterns: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "project_name": self.project_name,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "original_requirements": self.original_requirements,
            "current_objectives": self.current_objectives,
            "architecture_decisions": self.architecture_decisions,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "key_functions": self.key_functions,
            "successful_patterns": self.successful_patterns,
            "failed_approaches": self.failed_approaches,
            "lessons_learned": self.lessons_learned,
            "milestones_completed": self.milestones_completed,
            "current_blockers": self.current_blockers,
            "next_steps": self.next_steps,
            "agent_specializations": self.agent_specializations,
            "handoff_patterns": self.handoff_patterns,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMemory':
        """Create from dictionary"""
        memory = cls(
            project_name=data["project_name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            original_requirements=data["original_requirements"],
        )
        memory.current_objectives = data.get("current_objectives", [])
        memory.architecture_decisions = data.get("architecture_decisions", [])
        memory.files_created = data.get("files_created", [])
        memory.files_modified = data.get("files_modified", [])
        memory.key_functions = data.get("key_functions", [])
        memory.successful_patterns = data.get("successful_patterns", [])
        memory.failed_approaches = data.get("failed_approaches", [])
        memory.lessons_learned = data.get("lessons_learned", [])
        memory.milestones_completed = data.get("milestones_completed", [])
        memory.current_blockers = data.get("current_blockers", [])
        memory.next_steps = data.get("next_steps", [])
        memory.agent_specializations = data.get("agent_specializations", {})
        memory.handoff_patterns = data.get("handoff_patterns", [])
        return memory

class MemoryManager:
    """Manages conversation history and project memory"""
    
    def __init__(self, project_name: str, memory_dir: str = "memory"):
        self.project_name = project_name
        self.memory_dir = memory_dir
        self.conversation_history: List[ConversationEntry] = []
        self.project_memory: Optional[ProjectMemory] = None
        
        # Memory configuration
        self.max_conversation_length = 50  # entries before summarization
        self.max_tokens_per_conversation = 10000  # rough token limit
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing memory
        self._load_project_memory()
    
    def _load_project_memory(self):
        """Load existing project memory from file"""
        memory_file = os.path.join(self.memory_dir, f"{self.project_name}_memory.json")
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    self.project_memory = ProjectMemory.from_dict(data)
                    print(f"📚 Loaded existing project memory for {self.project_name}")
            except Exception as e:
                print(f"⚠️  Error loading project memory: {e}")
                self._create_new_project_memory()
        else:
            self._create_new_project_memory()
    
    def _create_new_project_memory(self):
        """Create new project memory"""
        now = datetime.now()
        self.project_memory = ProjectMemory(
            project_name=self.project_name,
            created_at=now,
            last_updated=now,
            original_requirements="",
        )
        print(f"🧠 Created new project memory for {self.project_name}")
    
    def save_project_memory(self):
        """Save project memory to file"""
        if self.project_memory:
            self.project_memory.last_updated = datetime.now()
            memory_file = os.path.join(self.memory_dir, f"{self.project_name}_memory.json")
            try:
                with open(memory_file, 'w') as f:
                    json.dump(self.project_memory.to_dict(), f, indent=2)
                print(f"💾 Saved project memory")
            except Exception as e:
                print(f"⚠️  Error saving project memory: {e}")
    
    def add_conversation_entry(self, agent_name: str, message_type: str, content: str, 
                             tokens_used: int = 0, metadata: Dict[str, Any] = None):
        """Add a conversation entry to history"""
        entry = ConversationEntry(
            timestamp=datetime.now(),
            agent_name=agent_name,
            message_type=message_type,
            content=content,
            tokens_used=tokens_used,
            metadata=metadata or {}
        )
        self.conversation_history.append(entry)
        
        # Check if we need to summarize
        if len(self.conversation_history) > self.max_conversation_length:
            self._summarize_conversation_history()
    
    def _summarize_conversation_history(self):
        """Summarize old conversation entries to save memory"""
        # Keep at least 3 entries for meaningful summarization
        min_entries_for_summary = min(10, max(3, self.max_conversation_length // 2))
        
        if len(self.conversation_history) <= min_entries_for_summary:
            return
        
        # Keep recent entries, summarize older ones
        keep_recent = min(10, self.max_conversation_length)
        recent_entries = self.conversation_history[-keep_recent:]
        older_entries = self.conversation_history[:-keep_recent]
        
        # Create summary of older entries
        summary_content = self._create_conversation_summary(older_entries)
        
        # Create a summary entry
        summary_entry = ConversationEntry(
            timestamp=datetime.now(),
            agent_name="MemoryManager",
            message_type="summary",
            content=summary_content,
            tokens_used=0,
            metadata={"summarized_entries": len(older_entries)}
        )
        
        # Replace old entries with summary
        self.conversation_history = [summary_entry] + recent_entries
        
        # Update project memory with key insights
        self._extract_insights_from_summary(summary_content)
        
        print(f"📝 Summarized {len(older_entries)} conversation entries")
    
    def _create_conversation_summary(self, entries: List[ConversationEntry]) -> str:
        """Create a summary of conversation entries"""
        if not entries:
            return "No conversation history to summarize."
        
        # Group entries by agent and type
        agent_activities = {}
        key_events = []
        
        for entry in entries:
            if entry.agent_name not in agent_activities:
                agent_activities[entry.agent_name] = []
            
            agent_activities[entry.agent_name].append(entry)
            
            # Identify key events
            if entry.message_type in ["handoff", "error"]:
                key_events.append(f"{entry.timestamp.strftime('%H:%M')} - {entry.agent_name}: {entry.message_type}")
        
        # Create summary
        summary_parts = [
            f"📊 CONVERSATION SUMMARY ({entries[0].timestamp.strftime('%H:%M')} - {entries[-1].timestamp.strftime('%H:%M')})",
            "",
            "🔄 Agent Activities:",
        ]
        
        for agent_name, agent_entries in agent_activities.items():
            activity_count = len(agent_entries)
            main_activities = [e.message_type for e in agent_entries]
            summary_parts.append(f"  • {agent_name}: {activity_count} activities ({', '.join(set(main_activities))})")
        
        if key_events:
            summary_parts.extend(["", "⚡ Key Events:"])
            summary_parts.extend([f"  • {event}" for event in key_events])
        
        return "\n".join(summary_parts)
    
    def _extract_insights_from_summary(self, summary: str):
        """Extract insights from conversation summary and update project memory"""
        if not self.project_memory:
            return
        
        # Simple pattern recognition for insights
        if "error" in summary.lower():
            self.project_memory.lessons_learned.append(f"Encountered errors during session at {datetime.now().strftime('%H:%M')}")
        
        if "handoff" in summary.lower():
            self.project_memory.handoff_patterns.append(f"Agent handoffs occurred at {datetime.now().strftime('%H:%M')}")
        
        # Update project memory
        self.save_project_memory()
    
    def get_context_summary(self) -> str:
        """Get a summary of current project context for agents"""
        if not self.project_memory:
            return "No project memory available."
        
        context_parts = [
            f"📁 PROJECT: {self.project_memory.project_name}",
            f"📅 Created: {self.project_memory.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"🎯 Requirements: {self.project_memory.original_requirements[:200]}...",
            "",
            "📂 Files Created:",
        ]
        
        for file in self.project_memory.files_created[-5:]:  # Show last 5 files
            context_parts.append(f"  • {file}")
        
        if self.project_memory.current_blockers:
            context_parts.extend(["", "🚫 Current Blockers:"])
            context_parts.extend([f"  • {blocker}" for blocker in self.project_memory.current_blockers])
        
        if self.project_memory.next_steps:
            context_parts.extend(["", "➡️  Next Steps:"])
            context_parts.extend([f"  • {step}" for step in self.project_memory.next_steps])
        
        return "\n".join(context_parts)
    
    def update_project_info(self, **kwargs):
        """Update project memory with new information"""
        if not self.project_memory:
            return
        
        for key, value in kwargs.items():
            if hasattr(self.project_memory, key):
                if isinstance(getattr(self.project_memory, key), list):
                    if isinstance(value, list):
                        getattr(self.project_memory, key).extend(value)
                    else:
                        getattr(self.project_memory, key).append(value)
                else:
                    setattr(self.project_memory, key, value)
        
        self.save_project_memory()

@dataclass
class ProjectContext:
    """Context shared across all agents with memory integration"""
    project_name: str
    requirements: str
    current_stage: str = "planning"
    files_created: List[str] = None
    test_results: Dict[str, Any] = None
    memory_manager: Optional[MemoryManager] = None
    
    def __post_init__(self):
        if self.files_created is None:
            self.files_created = []
        if self.test_results is None:
            self.test_results = {}
        if self.memory_manager is None:
            self.memory_manager = MemoryManager(self.project_name)
            # Initialize project memory with requirements
            self.memory_manager.update_project_info(original_requirements=self.requirements)

class StateManagementHooks(RunHooks):
    """Enhanced hooks with memory management"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
    
    async def on_handoff(self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent) -> None:
        print(f"🔄 Handoff from {from_agent.name} to {to_agent.name}")
        
        # Record handoff in memory
        self.memory_manager.add_conversation_entry(
            agent_name=from_agent.name,
            message_type="handoff",
            content=f"Handed off to {to_agent.name}",
            metadata={"to_agent": to_agent.name}
        )
        
        # Update project memory
        self.memory_manager.update_project_info(
            handoff_patterns=f"{from_agent.name} → {to_agent.name} at {datetime.now().strftime('%H:%M')}"
        )
    
    async def on_run_start(self, context: RunContextWrapper) -> None:
        print(f"🚀 Starting run with memory management")
        
        # Record run start
        self.memory_manager.add_conversation_entry(
            agent_name="System",
            message_type="run_start",
            content="Multi-agent system started",
            metadata={"context": str(context)}
        )
    
    async def on_run_end(self, context: RunContextWrapper) -> None:
        print(f"✅ Run completed - saving memory")
        
        # Record run end
        self.memory_manager.add_conversation_entry(
            agent_name="System",
            message_type="run_end",
            content="Multi-agent system completed",
            metadata={"context": str(context)}
        )
        
        # Final memory save
        self.memory_manager.save_project_memory()
    
    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool) -> None:
        """Track tool calls, especially file operations"""
        tool_name = getattr(tool, 'name', str(tool))
        print(f"🔧 Tool started: {tool_name}")
        
        # Record tool call
        self.memory_manager.add_conversation_entry(
            agent_name=agent.name,
            message_type="tool_call",
            content=f"Started tool: {tool_name}",
            metadata={"tool_name": tool_name, "agent": agent.name}
        )
    
    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool, result: str) -> None:
        """Track tool completion and extract file creation information"""
        tool_name = getattr(tool, 'name', str(tool))
        print(f"✅ Tool completed: {tool_name}")
        
        # Record tool completion
        self.memory_manager.add_conversation_entry(
            agent_name=agent.name,
            message_type="tool_result",
            content=f"Completed tool: {tool_name}",
            metadata={"tool_name": tool_name, "agent": agent.name, "result_length": len(result)}
        )
        
        # Track file creation specifically
        if "create_file" in tool_name.lower() or "filetool_create" in tool_name.lower():
            # Try to extract file path from result or tool attributes
            file_path = self._extract_file_path_from_result(result, tool_name)
            
            if file_path:
                print(f"📁 File created: {file_path}")
                self.memory_manager.update_project_info(files_created=file_path)
                
                # Record file creation event
                self.memory_manager.add_conversation_entry(
                    agent_name=agent.name,
                    message_type="file_created",
                    content=f"Created file: {file_path}",
                    metadata={"file_path": file_path, "tool_name": tool_name}
                )
        
        # Track file modification
        elif "edit_file" in tool_name.lower() or "filetool_edit" in tool_name.lower():
            file_path = self._extract_file_path_from_result(result, tool_name)
            
            if file_path:
                print(f"✏️ File modified: {file_path}")
                self.memory_manager.update_project_info(files_modified=file_path)
                
                # Record file modification event
                self.memory_manager.add_conversation_entry(
                    agent_name=agent.name,
                    message_type="file_modified",
                    content=f"Modified file: {file_path}",
                    metadata={"file_path": file_path, "tool_name": tool_name}
                )
    
    def _extract_file_path_from_result(self, result: str, tool_name: str) -> str:
        """Extract file path from tool result or name"""
        # Try to extract from common result patterns
        import re
        
        # Common file extensions
        extensions = r"(?:py|js|ts|tsx|jsx|md|txt|json|yaml|yml|html|css|cpp|c|java|rb|go|rs|php|sh|sql|xml|csv|log|cfg|ini|conf|env)"
        
        # Pattern 1: "Created file: /path/to/file.py" or "Modified file: filename.ext"
        pattern1 = rf"(?:Created|Modified|Wrote to|Saved)\s+(?:file:?\s+)?([^\s'\"]+\.{extensions})"
        match1 = re.search(pattern1, result, re.IGNORECASE)
        if match1:
            return match1.group(1).strip()
        
        # Pattern 2: File path in single quotes
        pattern2 = rf"'([^']+\.{extensions})'"
        match2 = re.search(pattern2, result, re.IGNORECASE)
        if match2:
            return match2.group(1).strip()
        
        # Pattern 3: File path in double quotes
        pattern3 = rf'"([^"]+\.{extensions})"'
        match3 = re.search(pattern3, result, re.IGNORECASE)
        if match3:
            return match3.group(1).strip()
        
        # Pattern 4: Simple filename patterns (more restrictive)
        pattern4 = rf"\b([a-zA-Z0-9_\-/\.]+\.{extensions})\b"
        match4 = re.search(pattern4, result, re.IGNORECASE)
        if match4:
            return match4.group(1).strip()
        
        return None

# Initialize Composio toolset
composio_toolset = ComposioToolSet()

# Python REPL tool (reused from toy example)
@function_tool
def run_python_code(code: str) -> str:
    """Execute Python code and return the output or error"""
    try:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        # Safe execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
        }
        
        exec(code, exec_globals)
        
        output = stdout_buffer.getvalue()
        error = stderr_buffer.getvalue()
        
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        if error:
            return f"Error: {error}"
        elif output:
            return f"Output: {output}"
        else:
            return "Code executed successfully (no output)"
            
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return f"Error: {str(e)}"

# Get file tools from Composio
file_tools = composio_toolset.get_tools(actions=[
    Action.FILETOOL_CREATE_FILE,
    Action.FILETOOL_EDIT_FILE,
    Action.FILETOOL_LIST_FILES,
])

# Create specialized agents with memory integration
def create_planner_agent() -> Agent[ProjectContext]:
    """Create the Planner agent with memory awareness"""
    return Agent(
        name="Planner",
        instructions="""
        You are a Senior Software Architect and Project Planner with access to project memory.
        
        MEMORY INTEGRATION:
        - Always start by reviewing the project context and memory
        - Check what has been done before to avoid duplication
        - Learn from previous approaches and failures
        - Update your planning based on project history
        
        Your responsibilities:
        1. Review project memory for context and history
        2. Analyze user requirements and break them down into specific, actionable tasks
        3. Create a development plan with clear steps
        4. Identify what files need to be created and what functionality is needed
        5. Provide estimates and suggest the order of implementation
        6. Hand off to the Coder agent when ready to implement
        
        Always be thorough in your planning and consider:
        - Code structure and organization
        - Error handling requirements
        - Testing approach
        - Documentation needs
        - Previous lessons learned
        - Architecture decisions made
        
        When you're ready to start implementation, hand off to the Coder agent.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Breaks down requirements into actionable development tasks with memory context",
        model="o4-mini",
        tools=file_tools,
    )

def create_coder_agent() -> Agent[ProjectContext]:
    """Create the Coder agent with memory awareness"""
    return Agent(
        name="Coder",
        instructions="""
        You are an Expert Software Developer with access to project memory and history.
        
        MEMORY INTEGRATION:
        - Review project memory for existing files and patterns
        - Learn from previous successful implementations
        - Avoid approaches that have failed before
        - Build on existing architecture decisions
        
        Your responsibilities:
        1. Review project memory for context and existing work
        2. Implement code based on the plan provided by the Planner
        3. Write clean, well-documented, and efficient code
        4. Follow best practices and coding standards
        5. Test your code as you write it using the Python REPL
        6. Create necessary files and organize code properly
        7. Hand off to the Reviewer agent when implementation is complete
        
        Always:
        - Write self-documenting code with clear variable names
        - Add appropriate comments and docstrings
        - Test your code thoroughly before handing off
        - Handle edge cases and errors gracefully
        - Follow Python best practices (PEP 8, etc.)
        - Learn from project history and memory
        
        When you've completed the implementation and tested it, hand off to the Reviewer.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Implements code based on the development plan with memory context",
        model="gpt-4.1",
        tools=[run_python_code] + file_tools,
    )

def create_reviewer_agent() -> Agent[ProjectContext]:
    """Create the Reviewer agent with memory awareness"""
    return Agent(
        name="Reviewer",
        instructions="""
        You are a Senior Code Reviewer and Quality Assurance Engineer with access to project memory.
        
        MEMORY INTEGRATION:
        - Review project memory for quality standards and patterns
        - Learn from previous review feedback and outcomes
        - Check consistency with architectural decisions
        - Validate against project requirements and history
        
        Your responsibilities:
        1. Review project memory for quality standards and context
        2. Review code for correctness, efficiency, and best practices
        3. Test the code thoroughly with various inputs
        4. Check for potential bugs, security issues, and edge cases
        5. Verify that the code meets the original requirements
        6. Provide feedback and suggestions for improvement
        7. Validate that tests pass and code works as expected
        8. Update project memory with lessons learned
        
        Review checklist:
        - Code functionality and correctness
        - Error handling and edge cases
        - Performance and efficiency
        - Security considerations
        - Code style and documentation
        - Test coverage
        - Consistency with project memory and decisions
        
        If issues are found, provide specific feedback and suggest fixes.
        If code is satisfactory, provide a summary and approve the implementation.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Reviews code quality and validates implementation with memory context",
        model="gpt-4.1-mini",
        tools=[run_python_code] + file_tools,
    )

def create_triage_agent() -> Agent[ProjectContext]:
    """Create the Triage agent with memory awareness"""
    
    # Create the specialized agents
    planner = create_planner_agent()
    coder = create_coder_agent()
    reviewer = create_reviewer_agent()
    
    # Set up handoffs between agents
    planner.handoffs = [handoff(coder)]
    coder.handoffs = [handoff(reviewer), handoff(planner)]
    reviewer.handoffs = [handoff(coder), handoff(planner)]
    
    return Agent(
        name="Triage",
        instructions="""
        You are the Project Manager and Workflow Orchestrator with access to project memory.
        
        MEMORY INTEGRATION:
        - Always start by reviewing project memory and context
        - Use historical information to make better routing decisions
        - Track workflow patterns and optimization opportunities
        - Maintain awareness of project progress and blockers
        
        Your job is to coordinate the software development process by routing tasks
        to the appropriate specialist agents:
        
        1. **Planner**: For breaking down requirements and creating development plans
        2. **Coder**: For implementing the actual code
        3. **Reviewer**: For code review and quality assurance
        
        When you receive a request:
        1. Review project memory for context and history
        2. Determine the current stage of the project
        3. Route to the appropriate agent
        4. Provide context and any relevant information
        5. Update memory with routing decisions
        
        Start with the Planner for new projects or requirements.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Orchestrates the development workflow with memory context",
        model="gpt-4.1",
        handoffs=[
            handoff(planner),
            handoff(coder),
            handoff(reviewer)
        ],
    )

async def run_multi_agent_system_with_memory(
    user_request: str,
    project_name: str = "MultiAgentProject"
) -> str:
    """
    Run the multi-agent system with memory management.
    
    This demonstrates the complete workflow with persistent memory.
    """
    print(f"🚀 Starting Multi-Agent Development System with Memory")
    print(f"📋 Project: {project_name}")
    print(f"🎯 Request: {user_request}")
    print("=" * 60)
    
    # Create project context with memory
    context = ProjectContext(
        project_name=project_name,
        requirements=user_request,
        current_stage="planning"
    )
    
    # Display memory context
    print(f"🧠 Memory Context:")
    print(context.memory_manager.get_context_summary())
    print("=" * 60)
    
    # Create the triage agent
    triage_agent = create_triage_agent()
    
    # Configure run settings
    run_config = RunConfig(
        workflow_name="Multi-Agent Development with Memory",
    )
    
    # Create memory-aware hooks
    hooks = StateManagementHooks(context.memory_manager)
    
    try:
        with trace("state-management-multi-agent"):
            # Run the multi-agent system
            result = await Runner.run(
                starting_agent=triage_agent,
                input=user_request,
                context=context,
                run_config=run_config,
                hooks=hooks,
                max_turns=50
            )
        
        # Update memory with final results
        context.memory_manager.update_project_info(
            milestones_completed=f"Completed request: {user_request[:100]}..."
        )
        
        return result.final_output
        
    except Exception as e:
        print(f"❌ Error running multi-agent system: {str(e)}")
        
        # Record error in memory
        context.memory_manager.add_conversation_entry(
            agent_name="System",
            message_type="error",
            content=f"System error: {str(e)}",
            metadata={"error_type": type(e).__name__}
        )
        
        return f"Error: {str(e)}"

async def demo_memory_workflow():
    """Demonstrate the memory-enabled workflow"""
    print("\n🧠 Demo: Memory-Enabled Multi-Agent Workflow")
    print("=" * 50)
    
    # First request - establishing project
    request1 = """
    Create a Python data processing system that:
    1. Reads CSV data from a file
    2. Performs data cleaning and validation
    3. Calculates statistical summaries
    4. Exports results to JSON format
    5. Includes comprehensive error handling
    
    The system should be modular and well-documented.
    """
    
    print("📝 First Request: Setting up data processing system...")
    result1 = await run_multi_agent_system_with_memory(request1, "DataProcessingProject")
    print(f"\n✅ First Result:\n{result1}")
    
    print("\n" + "="*60)
    
    # Second request - building on previous work
    request2 = """
    Now add advanced features to the data processing system:
    1. Add data visualization capabilities with matplotlib
    2. Include more sophisticated statistical analysis
    3. Add configuration file support
    4. Create a command-line interface
    5. Add logging and monitoring
    
    Build on the existing system architecture.
    """
    
    print("📝 Second Request: Enhancing the system...")
    result2 = await run_multi_agent_system_with_memory(request2, "DataProcessingProject")
    print(f"\n✅ Second Result:\n{result2}")

async def main():
    """Main function to run memory-enabled demonstrations"""
    print("🤖 Multi-Agent Software Development System with Memory")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    demos = [
        ("Memory Workflow", demo_memory_workflow),
    ]
    
    for demo_name, demo_func in demos:
        try:
            await demo_func()
            print(f"\n✅ {demo_name} completed successfully!")
        except Exception as e:
            print(f"\n❌ {demo_name} failed: {str(e)}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main()) 