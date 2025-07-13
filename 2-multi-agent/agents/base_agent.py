"""
Base Agent Class

This module provides the foundation for all specialized agents in the multi-agent system.
It handles common functionality like OpenAI API calls, tool integration, and message formatting.
"""

import json
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from openai import OpenAI
from composio_openai import ComposioToolSet, Action


@dataclass
class AgentMessage:
    """Represents a message between agents"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    agent_name: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """Represents the result of an agent's work"""
    success: bool
    content: str
    agent_name: str
    model_used: str
    metadata: Optional[Dict[str, Any]] = None
    messages: Optional[List[AgentMessage]] = None


class BaseAgent(ABC):
    """
    Base class for all specialized agents.
    
    This class provides common functionality:
    - OpenAI API integration
    - Tool calling capabilities
    - Message formatting and handling
    - Error handling and logging
    """
    
    def __init__(
        self,
        name: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        client: Optional[OpenAI] = None
    ):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = client or OpenAI()
        self.composio_toolset = ComposioToolSet()
        
        # Initialize tools
        self.tools = self._get_tools()
        
        # Message history for this agent
        self.messages: List[AgentMessage] = []
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Return the tools this agent can use"""
        pass
    
    def _create_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> AgentMessage:
        """Create a formatted message"""
        return AgentMessage(
            role=role,
            content=content,
            agent_name=self.name,
            metadata=metadata or {}
        )
    
    def _format_messages_for_openai(self, messages: List[AgentMessage]) -> List[Dict[str, str]]:
        """Format messages for OpenAI API"""
        formatted = []
        
        # Add system message
        formatted.append({
            "role": "system",
            "content": self._get_system_prompt()
        })
        
        # Add conversation messages
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return formatted
    
    def _handle_tool_call(self, tool_call) -> str:
        """Handle a tool call and return the result"""
        function_name = tool_call.function.name
        
        try:
            function_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in tool call arguments"
        
        # Handle Python REPL tool (if available)
        if function_name == "run_python_code":
            from ..utils.python_repl import run_python_code
            return run_python_code(function_args.get("code", ""))
        
        # Handle Composio file tools
        try:
            result = self.composio_toolset.handle_tool_call(tool_call)
            return str(result)
        except Exception as e:
            return f"Error executing tool {function_name}: {str(e)}"
    
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Run the agent on a given task.
        
        Args:
            task: The task for the agent to perform
            context: Optional context from previous agents
            
        Returns:
            AgentResult with the agent's response
        """
        # Create user message
        user_message = self._create_message("user", task)
        messages = [user_message]
        
        # Add context if provided
        if context:
            context_msg = self._create_message(
                "user", 
                f"Context from previous agents: {json.dumps(context, indent=2)}"
            )
            messages.insert(0, context_msg)
        
        try:
            # Format messages for OpenAI
            formatted_messages = self._format_messages_for_openai(messages)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                tools=self.tools if self.tools else None,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            response_message = response.choices[0].message
            
            # Handle tool calls if present
            if response_message.tool_calls:
                messages.append(self._create_message("assistant", response_message.content or ""))
                
                for tool_call in response_message.tool_calls:
                    tool_result = self._handle_tool_call(tool_call)
                    messages.append(self._create_message("tool", tool_result))
                
                # Get final response after tool calls
                formatted_messages = self._format_messages_for_openai(messages)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=formatted_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                final_content = response.choices[0].message.content
            else:
                final_content = response_message.content
            
            # Store messages for this interaction
            self.messages.extend(messages)
            
            return AgentResult(
                success=True,
                content=final_content or "",
                agent_name=self.name,
                model_used=self.model,
                messages=messages
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                content=f"Error: {str(e)}",
                agent_name=self.name,
                model_used=self.model,
                messages=messages
            )
    
    def handoff_to(self, other_agent: 'BaseAgent', task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Hand off a task to another agent.
        
        Args:
            other_agent: The agent to hand off to
            task: The task to hand off
            context: Context to pass to the other agent
            
        Returns:
            AgentResult from the other agent
        """
        # Add this agent's context to the handoff
        handoff_context = context or {}
        handoff_context[f"{self.name}_context"] = {
            "agent_name": self.name,
            "model_used": self.model,
            "recent_messages": [asdict(msg) for msg in self.messages[-3:]]  # Last 3 messages
        }
        
        print(f"🔄 {self.name} handing off to {other_agent.name}")
        return other_agent.run(task, handoff_context)
    
    def clear_history(self):
        """Clear the message history for this agent"""
        self.messages.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": self.name,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "message_count": len(self.messages)
        } 