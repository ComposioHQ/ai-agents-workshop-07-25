#!/usr/bin/env python3
"""
Simple Coding Agent - Workshop Toy Example

This is a basic coding agent that can:
1. Write Python code based on natural language requests
2. Execute Python code using a REPL tool
3. Create, edit, and manage files using Composio's file tools
4. Provide feedback and iterate on code

Usage:
    python coding_agent.py "Create a Python function to check if a number is prime and test it on 7"
"""

import sys
import os
from typing import Dict, Any
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import OpenAI Agents SDK
from openai import OpenAI
from composio_openai import ComposioToolSet, Action

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup Composio toolset for file operations
composio_toolset = ComposioToolSet()

def run_python_code(code: str) -> str:
    """
    Execute Python code and return the output or error.
    This is our simple REPL tool.
    """
    try:
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        
        # Redirect output
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        # Create a safe execution environment
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
        
        # Execute the code
        exec(code, exec_globals)
        
        # Get the output
        output = stdout_buffer.getvalue()
        error = stderr_buffer.getvalue()
        
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        if error:
            return f"Error: {error}"
        elif output:
            return f"Output: {output}"
        else:
            return "Code executed successfully (no output)"
            
    except Exception as e:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return f"Error: {str(e)}"

def create_coding_agent():
    """Create and configure the coding agent with tools"""
    
    # Get Composio file tools
    file_tools = composio_toolset.get_tools(actions=[
        Action.FILETOOL_CREATE_FILE,
        Action.FILETOOL_EDIT_FILE,
        Action.FILETOOL_LIST_FILES,
    ])
    
    # Define the Python REPL tool
    python_repl_tool = {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": "Execute Python code and return the output or error",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }
    }
    
    # System instructions for the agent
    system_instructions = """
You are a helpful coding agent that can write, execute, and manage Python code.

Your capabilities include:
1. Writing Python functions and scripts based on natural language requests
2. Executing Python code using the run_python_code tool to test and validate your solutions
3. Creating, editing, and managing files using the file tools
4. Providing clear explanations of your code and test results

When asked to create a function:
1. First, write the function code
2. Then, create test cases to verify it works correctly
3. Execute the code to show the results
4. Always save the code to a file (example: "my_function.py")

Always explain what you're doing and why, and make sure to test your code thoroughly.
"""
    
    return {
        "model": "gpt-4.1",
        "tools": [python_repl_tool] + file_tools,
        "system_instructions": system_instructions
    }

def run_agent(user_request: str) -> str:
    """Run the coding agent with a user request"""
    
    # Create the agent configuration
    agent_config = create_coding_agent()
    
    # Create the conversation
    messages = [
        {"role": "system", "content": agent_config["system_instructions"]},
        {"role": "user", "content": user_request}
    ]
    
    print(f"🤖 Agent: Processing request: {user_request}")
    print("=" * 50)
    
    # Run the conversation loop
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # Get response from the model
        response = client.chat.completions.create(
            model=agent_config["model"],
            messages=messages,
            tools=agent_config["tools"],
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        # Check if the model wants to call a function
        if response_message.tool_calls:
            print(f"🔧 Agent is calling tools...")
            
            # Handle each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)
                
                print(f"   Calling: {function_name}")
                
                # Handle our custom Python REPL tool
                if function_name == "run_python_code":
                    result = run_python_code(function_args["code"])
                    print(f"   Code executed:")
                    print(f"   {function_args['code']}")
                    print(f"   Result: {result}")
                
                # Handle Composio file tools
                else:
                    try:
                        result = composio_toolset.handle_tool_calls(tool_call)
                        print(f"   Result: {result}")
                    except Exception as e:
                        result = f"Error: {str(e)}"
                        print(f"   Error: {result}")
                
                # Add the tool result to the conversation
                messages.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call.id
                })
        else:
            # No more tool calls, agent is done
            print(f"\n🎉 Agent: {response_message.content}")
            return response_message.content
    
    return "Maximum iterations reached. Agent may need more time to complete the task."

def main():
    """Main function to run the coding agent"""
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    # Get user request from command line or use default
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = "Create a Python function that checks if a number is prime and test it on the number 7"
    
    print("🚀 Starting Coding Agent - Toy Example")
    print("=" * 50)
    
    try:
        # Run the agent
        result = run_agent(user_request)
        
        print("\n" + "=" * 50)
        print("✅ Agent completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 