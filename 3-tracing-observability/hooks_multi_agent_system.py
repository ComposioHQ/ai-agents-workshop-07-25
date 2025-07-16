#!/usr/bin/env python3
"""
Multi-Agent Software Development System

This demonstrates a production-ready multi-agent system with:
1. Specialized agents for different tasks
2. Handoff mechanisms between agents
3. Cost optimization using different models
4. Composio tool integration
5. Practical software development workflow
"""

import os
import sys
import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# OpenAI Agents SDK imports
from agents import Agent, Runner, handoff, RunConfig, function_tool, trace, RunHooks, RunContextWrapper
# Composio imports
from composio_openai_agents import ComposioToolSet, Action, App

# Load environment variables
load_dotenv()

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

class HandoffHooks(RunHooks):
    async def on_handoff(self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent) -> None:
        print(f"Handoff from {from_agent.name} to {to_agent.name}")

# Create specialized agents
def create_planner_agent() -> Agent:
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
        model="o4-mini",  # Use reasoing model for planning
        tools=file_tools,  # Can read existing files for context
    )

def create_coder_agent() -> Agent:
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
        tools=[run_python_code] + file_tools,
    )

def create_reviewer_agent() -> Agent:
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
        tools=[run_python_code] + file_tools,
    )

def create_triage_agent() -> Agent:
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
        
        When you receive a request:
        1. Determine the current stage of the project
        2. Route to the appropriate agent
        3. Provide context and any relevant information
        
        Start with the Planner for new projects or requirements.

        IMPORTANT:
        You are working autonomously. You are not allowed to ask the user for any information or consent.
        """,
        handoff_description="Orchestrates the development workflow",
        model="gpt-4.1",  # Use standard model for orchestration
        handoffs=[
            handoff(planner),
            handoff(coder),
            handoff(reviewer)
        ],
    )

async def run_multi_agent_system(
    user_request: str,
    project_name: str = "MultiAgentProject"
) -> str:
    """
    Run the multi-agent system with a user request.
    
    This demonstrates the complete workflow from planning to implementation to review.
    """
    print(f"🚀 Starting Multi-Agent Development System")
    print(f"📋 Project: {project_name}")
    print(f"🎯 Request: {user_request}")
    print("=" * 60)
    
    # Create the triage agent
    triage_agent = create_triage_agent()
    
    # Configure run settings
    run_config = RunConfig(
        workflow_name="Multi-Agent Development",
    )
    
    try:
        with trace("tracing-multi-agent-coder"):
            # Run the multi-agent system
            result = await Runner.run(
                starting_agent=triage_agent,
                input=user_request,
                run_config=run_config,
                hooks=HandoffHooks(),
                max_turns=50  # Allow for multiple handoffs
            )
        
        return result.final_output
        
    except Exception as e:
        print(f"❌ Error running multi-agent system: {str(e)}")
        return f"Error: {str(e)}"

async def demo_workflow():
    """Demonstrate complex multi-agent workflow with multiple features"""
    print("\n🎯 Demo 1: Complex Data Processing System")
    print("=" * 50)
    
    request = """
    Create a Python data processing system that:
    1. Reads CSV data from a file
    2. Performs data cleaning and validation
    3. Calculates statistical summaries
    4. Exports results to JSON format
    5. Includes comprehensive error handling
    
    The system should be modular and well-documented.
    """
    
    result = await run_multi_agent_system(request, "DataProcessingProject")
    print(f"\n✅ Final Result:\n{result}")

async def main():
    """Main function to run all demonstrations"""
    print("🤖 Multi-Agent Software Development System")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    demos = [
        ("Workflow", demo_workflow),
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