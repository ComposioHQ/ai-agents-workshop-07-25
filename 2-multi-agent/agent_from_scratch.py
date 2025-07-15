#!/usr/bin/env python3
"""
Agent Implementation From Scratch

This module shows how AI agents work under the hood by implementing
a basic agent without using the OpenAI Agents SDK. This is for educational
purposes to understand the core concepts before using the SDK.
"""

import json
import os
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

@dataclass
class ToolCall:
    """Represents a tool call"""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ToolResult:
    """Represents the result of a tool call"""
    tool_call_id: str
    content: str

class BasicAgent:
    """
    A basic AI agent implementation from scratch.
    
    This shows the core concepts:
    1. System instructions (prompt)
    2. Tool calling
    3. Conversation loop
    4. State management
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        tools: Optional[List[Callable]] = None,
        model: str = "gpt-4.1-mini"  # Use cheaper model for demo
    ):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history: List[Message] = []
        
        # Create tool schemas for OpenAI
        self.tool_schemas = self._create_tool_schemas()
        
        # Initialize with system message
        self.conversation_history.append(
            Message(role="system", content=instructions)
        )
    
    def _create_tool_schemas(self) -> List[Dict[str, Any]]:
        """Convert Python functions to OpenAI tool schemas"""
        schemas = []
        
        for tool in self.tools:
            # Extract function signature and docstring
            import inspect
            
            sig = inspect.signature(tool)
            doc = inspect.getdoc(tool) or "No description available"
            
            # Create basic schema
            schema = {
                "type": "function",
                "function": {
                    "name": tool.__name__,
                    "description": doc,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # Add parameters from signature
            for param_name, param in sig.parameters.items():
                if param_name != 'self':  # Skip self parameter
                    schema["function"]["parameters"]["properties"][param_name] = {
                        "type": "string",  # Simplified - in real implementation would infer type
                        "description": f"Parameter {param_name}"
                    }
                    
                    if param.default == inspect.Parameter.empty:
                        schema["function"]["parameters"]["required"].append(param_name)
            
            schemas.append(schema)
        
        return schemas
    
    def _execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call and return the result"""
        # Find the tool function
        tool_func = None
        for tool in self.tools:
            if tool.__name__ == tool_call.name:
                tool_func = tool
                break
        
        if not tool_func:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=f"Error: Tool '{tool_call.name}' not found"
            )
        
        try:
            # Call the tool function
            result = tool_func(**tool_call.arguments)
            return ToolResult(
                tool_call_id=tool_call.id,
                content=str(result)
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=f"Error executing tool: {str(e)}"
            )
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        self.conversation_history.append(
            Message(role=role, content=content)
        )
    
    def run(self, user_input: str, max_iterations: int = 10) -> str:
        """
        Run the agent with user input.
        
        This is the core agent loop:
        1. Add user message
        2. Call LLM
        3. If tool calls, execute them and repeat
        4. Return final response
        """
        # Add user message
        self.add_message("user", user_input)
        
        for iteration in range(max_iterations):
            print(f"\n--- Agent Iteration {iteration + 1} ---")
            
            # Convert conversation history to OpenAI format
            messages = []
            for msg in self.conversation_history:
                openai_msg = {
                    "role": msg.role,
                    "content": msg.content
                }
                if msg.tool_calls:
                    openai_msg["tool_calls"] = msg.tool_calls
                if msg.tool_call_id:
                    openai_msg["tool_call_id"] = msg.tool_call_id
                messages.append(openai_msg)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_schemas if self.tool_schemas else None,
                tool_choice="auto" if self.tool_schemas else None
            )
            
            response_message = response.choices[0].message
            
            # Add assistant response to history
            assistant_msg = Message(
                role="assistant",
                content=response_message.content or ""
            )
            
            # Check if there are tool calls
            if response_message.tool_calls:
                print(f"Agent wants to call {len(response_message.tool_calls)} tools")
                
                # Add tool calls to message
                assistant_msg.tool_calls = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response_message.tool_calls
                ]
                self.conversation_history.append(assistant_msg)
                
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    print(f"Executing tool: {tool_call.function.name}")
                    
                    # Parse arguments
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        arguments = {}
                        print(f"Error parsing tool arguments: {e}")
                    
                    # Execute tool
                    tool_result = self._execute_tool(ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=arguments
                    ))
                    
                    # Add tool result to conversation
                    self.conversation_history.append(Message(
                        role="tool",
                        content=tool_result.content,
                        tool_call_id=tool_result.tool_call_id
                    ))
                    
                    print(f"Tool result: {tool_result.content[:100]}...")
                
                # Continue the loop to get the final response
                continue
            
            else:
                # No tool calls, this is the final response
                self.conversation_history.append(assistant_msg)
                print(f"Agent response: {response_message.content}")
                return response_message.content
        
        return "Maximum iterations reached"
    
    def get_conversation_history(self) -> List[Message]:
        """Get the current conversation history"""
        return self.conversation_history.copy()
    
    def reset_conversation(self) -> None:
        """Reset the conversation history (keep system message)"""
        self.conversation_history = [
            Message(role="system", content=self.instructions)
        ]

# Example tools for demonstration
def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely"""
    try:
        # Simple calculator - in production, use ast.literal_eval or similar
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_current_time() -> str:
    """Get the current time"""
    from datetime import datetime
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def write_to_file(filename: str, content: str) -> str:
    """Write content to a file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

# Example usage
def main():
    print("🔧 Basic Agent From Scratch Demo")
    print("=" * 50)
    
    # Create an agent with tools
    agent = BasicAgent(
        name="Math Assistant",
        instructions="You are a helpful math assistant. You can calculate expressions and write results to files.",
        tools=[calculate, get_current_time, write_to_file]
    )
    
    # Example interactions
    examples = [
        "What is 15 * 8 + 7?",
        "Calculate the square root of 144 and write the result to result.txt",
        "What time is it now?"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*50}")
        print(f"Example {i}: {example}")
        print(f"{'='*50}")
        
        response = agent.run(example)
        print(f"\nFinal Response: {response}")
        
        # Reset for next example
        agent.reset_conversation()

if __name__ == "__main__":
    main() 