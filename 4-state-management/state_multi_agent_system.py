#!/usr/bin/env python3
"""
Multi-Agent Software Development System with State Management

This demonstrates a production-ready multi-agent system with:
1. Specialized agents for different tasks
2. Handoff mechanisms between agents
3. Cost optimization using different models
4. Composio tool integration
5. Practical software development workflow
6. STATE MANAGEMENT:
   - OpenAI Agents SDK Sessions for conversation memory across runs
   - File tracking hooks to prevent duplicate file creation
   - Simple memory layer with summarization
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime

# OpenAI Agents SDK imports
from agents import Agent, Runner, Tool, handoff, RunConfig, function_tool, trace, RunHooks, RunContextWrapper, SQLiteSession
# Composio imports
from composio_openai_agents import ComposioToolSet, Action, App

# Load environment variables
load_dotenv()

@dataclass
class ProjectContext:
    """Context shared across all agents with state management"""
    project_name: str
    requirements: str
    current_stage: str = "planning"
    files_created: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    session_id: str = "default"
    memory_file: str = "memory.json"
    
    def __post_init__(self):
        # Ensure memory file exists
        if not os.path.exists(self.memory_file):
            self.save_memory({"conversations": [], "files_created": [], "project_summary": ""})
    
    def save_memory(self, data: Dict[str, Any]):
        """Save data to memory file"""
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_memory(self) -> Dict[str, Any]:
        """Load data from memory file"""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"conversations": [], "files_created": [], "project_summary": ""}
    
    def add_conversation_summary(self, summary: str):
        """Add conversation summary to memory"""
        memory = self.load_memory()
        memory["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        })
        self.save_memory(memory)
    
    def update_project_summary(self, summary: str):
        """Update project summary in memory"""
        memory = self.load_memory()
        memory["project_summary"] = summary
        self.save_memory(memory)

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

class StateManagementHooks(RunHooks):
    """Enhanced hooks with state management features"""
    
    def __init__(self, context: ProjectContext):
        self.context = context
        
    async def on_handoff(self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent) -> None:
        print(f"🔄 Handoff from {from_agent.name} to {to_agent.name}")
    
    async def on_tool_call_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str) -> None:
        """Track file creation to prevent duplicates"""
        print(f"🔄 Tool call end: {tool.name}")
        if tool.name == 'filetool_create_file':
            try:
                # Parse the arguments to get filename
                args = json.loads(tool.arguments)
                filename = args.get('file_path', '')
                
                if filename and filename not in self.context.files_created:
                    self.context.files_created.append(filename)
                    print(f"📄 File created: {filename}")
                    
                    # Update memory with created files
                    memory = self.context.load_memory()
                    if filename not in memory["files_created"]:
                        memory["files_created"].append(filename)
                        self.context.save_memory(memory)
                        
            except (json.JSONDecodeError, KeyError):
                pass  # Ignore parsing errors

@function_tool
def check_file_exists(context: RunContextWrapper[ProjectContext], filename: str) -> str:
    """Check if a file was already created to prevent duplicates"""
    if filename in context.context.files_created:
        return f"File {filename} already exists in this session"
    
    memory = context.context.load_memory()
    if filename in memory["files_created"]:
        return f"File {filename} was created in a previous session"
    
    return f"File {filename} does not exist yet"

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

@function_tool
def summarize_session(context: RunContextWrapper[ProjectContext], summary: str) -> str:
    """Summarize the current session for future reference"""
    context.context.add_conversation_summary(summary)
    return f"Session summary saved: {summary}"

# Create specialized agents with state management
def create_planner_agent() -> Agent[ProjectContext]:
    """Create the Planner agent - breaks down requirements into tasks"""
    return Agent(
        name="Planner",
        instructions="""
        You are a Senior Software Architect and Project Planner.
        
        Your responsibilities:
        1. Analyze user requirements and break them down into specific, actionable tasks
        2. Create a development plan with clear steps
        3. Identify what files need to be created and what functionality is needed
        4. Provide estimates and suggest the order of implementation
        5. Hand off to the Coder agent when ready to implement
        
        IMPORTANT STATE MANAGEMENT:
        - Always check project memory first to understand what has been done before
        - Use check_file_exists before planning to create files
        - Consider past conversations when planning
        - Summarize your planning session before handing off
        
        Always be thorough in your planning and consider:
        - Code structure and organization
        - Error handling requirements
        - Testing approach
        - Documentation needs
        
        When you're ready to start implementation, hand off to the Coder agent.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Breaks down requirements into actionable development tasks",
        model="o4-mini",  # Use reasoning model for planning
        tools=file_tools + [check_file_exists, get_project_memory, summarize_session],
    )

def create_coder_agent() -> Agent[ProjectContext]:
    """Create the Coder agent - implements the actual code"""
    return Agent(
        name="Coder",
        instructions="""
        You are an Expert Software Developer.
        
        Your responsibilities:
        1. Implement code based on the plan provided by the Planner
        2. Write clean, well-documented, and efficient code
        3. Follow best practices and coding standards
        4. Test your code as you write it using the Python REPL
        5. Create necessary files and organize code properly
        6. Hand off to the Reviewer agent when implementation is complete
        
        IMPORTANT STATE MANAGEMENT:
        - Check project memory to understand what has been done before
        - Use check_file_exists before creating files to avoid duplicates
        - Build upon existing files rather than recreating them
        - Summarize your coding session before handing off
        
        Always:
        - Write self-documenting code with clear variable names
        - Add appropriate comments and docstrings
        - Test your code thoroughly before handing off
        - Handle edge cases and errors gracefully
        - Follow Python best practices (PEP 8, etc.)
        
        When you've completed the implementation and tested it, hand off to the Reviewer.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Implements code based on the development plan",
        model="gpt-4.1",  # Use coding model for coding
        tools=[run_python_code] + file_tools + [check_file_exists, get_project_memory, summarize_session],
    )

def create_reviewer_agent() -> Agent[ProjectContext]:
    """Create the Reviewer agent - reviews and validates code"""
    return Agent(
        name="Reviewer",
        instructions="""
        You are a Senior Code Reviewer and Quality Assurance Engineer.
        
        Your responsibilities:
        1. Review code for correctness, efficiency, and best practices
        2. Test the code thoroughly with various inputs
        3. Check for potential bugs, security issues, and edge cases
        4. Verify that the code meets the original requirements
        5. Provide feedback and suggestions for improvement
        6. Validate that tests pass and code works as expected
        
        IMPORTANT STATE MANAGEMENT:
        - Check project memory to understand the full context
        - Review all created files to ensure consistency
        - Consider past conversations when reviewing
        - Summarize your review session for future reference
        
        Review checklist:
        - Code functionality and correctness
        - Error handling and edge cases
        - Performance and efficiency
        - Security considerations
        - Code style and documentation
        - Test coverage
        
        If issues are found, provide specific feedback and suggest fixes.
        If code is satisfactory, provide a summary and approve the implementation.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Reviews code quality and validates implementation",
        model="gpt-4.1-mini",  # Use cheaper model for review
        tools=[run_python_code] + file_tools + [check_file_exists, get_project_memory, summarize_session],
    )

def create_triage_agent() -> Agent[ProjectContext]:
    """Create the Triage agent - orchestrates the workflow"""
    
    # Create the specialized agents
    planner = create_planner_agent()
    coder = create_coder_agent()
    reviewer = create_reviewer_agent()
    
    # Set up handoffs between agents
    planner.handoffs = [handoff(coder)]
    coder.handoffs = [handoff(reviewer), handoff(planner)]  # Can go back to planner if needed
    reviewer.handoffs = [handoff(coder), handoff(planner)]  # Can send back for fixes
    
    return Agent(
        name="Triage",
        instructions="""
        You are the Project Manager and Workflow Orchestrator.
        
        Your job is to coordinate the software development process by routing tasks
        to the appropriate specialist agents:
        
        1. **Planner**: For breaking down requirements and creating development plans
        2. **Coder**: For implementing the actual code
        3. **Reviewer**: For code review and quality assurance
        
        IMPORTANT STATE MANAGEMENT:
        - Always check project memory first to understand what has been done before
        - Consider past conversations when routing tasks
        - Update project summary after major milestones
        
        When you receive a request:
        1. Check project memory to understand current state
        2. Determine the current stage of the project
        3. Route to the appropriate agent
        4. Provide context and any relevant information
        
        Start with the Planner for new projects or requirements.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Orchestrates the development workflow",
        model="gpt-4.1",  # Use standard model for orchestration
        tools=[get_project_memory, summarize_session],
        handoffs=[
            handoff(planner),
            handoff(coder),
            handoff(reviewer)
        ],
    )

async def run_multi_agent_system_with_state(
    user_request: str,
    project_name: str = "MultiAgentProject",
    session_id: str = "default"
) -> str:
    """
    Run the multi-agent system with state management.
    
    This demonstrates the complete workflow with:
    - Conversation memory across runs using OpenAI Agents SDK Sessions
    - File tracking to prevent duplicates
    - Simple memory layer with summarization
    """
    print(f"🚀 Starting Multi-Agent Development System with State Management")
    print(f"📋 Project: {project_name}")
    print(f"🔗 Session: {session_id}")
    print(f"🎯 Request: {user_request}")
    print("=" * 60)
    
    # Create project context with state management
    context = ProjectContext(
        project_name=project_name,
        requirements=user_request,
        current_stage="planning",
        session_id=session_id,
        memory_file=f"memory_{session_id}.json"
    )
    
    # Create session for conversation memory
    session = SQLiteSession(session_id)
    
    # Create the triage agent
    triage_agent = create_triage_agent()
    
    # Create hooks for state management
    hooks = StateManagementHooks(context)
    
    # Configure run settings
    run_config = RunConfig(
        workflow_name="Multi-Agent Development with State",
    )
    
    try:
        with trace("state-management-multi-agent"):
            # Run the multi-agent system with session for conversation memory
            result = await Runner.run(
                starting_agent=triage_agent,
                input=user_request,
                context=context,
                session=session,  # This enables conversation memory across runs
                run_config=run_config,
                hooks=hooks,
                max_turns=50  # Allow for multiple handoffs
            )
        
        # Generate a summary of this session
        session_summary = f"Completed request: {user_request[:100]}... Final output: {result.final_output[:200]}..."
        context.add_conversation_summary(session_summary)
        
        print(f"\n💾 Session saved to memory for future reference")
        print(f"📁 Files created this session: {context.files_created}")
        
        return result.final_output
        
    except Exception as e:
        print(f"❌ Error running multi-agent system: {str(e)}")
        return f"Error: {str(e)}"

async def demo_state_management():
    """Demonstrate state management features"""
    print("\n🎯 Demo: State Management Features")
    print("=" * 50)
    
    session_id = "demo_session"
    
    # First request - creates some files
    print("\n📝 First Request:")
    request1 = """
    Create a simple Python calculator that:
    1. Has functions for basic operations (+, -, *, /)
    2. Includes error handling for division by zero
    3. Has a simple CLI interface
    """
    
    result1 = await run_multi_agent_system_with_state(request1, "CalculatorProject", session_id)
    print(f"\n✅ First Result:\n{result1}")
    
    # Second request - should remember the previous conversation
    print("\n📝 Second Request (should remember previous context):")
    request2 = """
    Now add a function to calculate the square root and modify the CLI to support it.
    """
    
    result2 = await run_multi_agent_system_with_state(request2, "CalculatorProject", session_id)
    print(f"\n✅ Second Result:\n{result2}")
    
    # Third request - should avoid recreating files
    print("\n📝 Third Request (should avoid recreating files):")
    request3 = """
    Create comprehensive unit tests for the calculator functions.
    """
    
    result3 = await run_multi_agent_system_with_state(request3, "CalculatorProject", session_id)
    print(f"\n✅ Third Result:\n{result3}")

async def main():
    """Main function to run all demonstrations"""
    print("🤖 Multi-Agent Software Development System with State Management")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    try:
        await demo_state_management()
        print(f"\n✅ Demo completed successfully!")
        print("\n🔍 State Management Features Demonstrated:")
        print("• OpenAI Agents SDK Sessions for conversation memory")
        print("• File tracking hooks to prevent duplicate creation")
        print("• Simple memory layer with JSON persistence")
        print("• Conversation summarization for future reference")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main()) 