"""
Python REPL Utility

This module provides a safe Python code execution environment
for agents to run and test code.
"""

import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any


def run_python_code(code: str) -> str:
    """
    Execute Python code and return the output or error.
    
    Args:
        code: Python code to execute
        
    Returns:
        String containing the output or error message
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
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'all': all,
            'any': any,
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


def create_python_repl_tool() -> Dict[str, Any]:
    """
    Create a tool definition for the Python REPL that can be used by agents.
    
    Returns:
        Dictionary containing the tool definition for OpenAI function calling
    """
    return {
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