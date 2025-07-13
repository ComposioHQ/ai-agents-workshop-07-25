"""
Coder Agent

This agent specializes in writing Python code based on specifications.
It uses GPT-4 for complex code generation and can execute code to verify functionality.
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent
from ..utils.python_repl import create_python_repl_tool


class CoderAgent(BaseAgent):
    """
    Agent that specializes in writing and implementing Python code.
    
    This agent:
    - Writes Python code based on specifications
    - Implements functions, classes, and modules
    - Tests code functionality using the Python REPL
    - Handles error correction and debugging
    - Follows best practices and coding standards
    """
    
    def __init__(self, **kwargs):
        # Use GPT-4 for complex code generation (default)
        kwargs.setdefault('model', 'gpt-4')
        kwargs.setdefault('name', 'Coder')
        kwargs.setdefault('temperature', 0.1)  # Lower temperature for more consistent code
        
        super().__init__(**kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are a Coder Agent, specialized in writing high-quality Python code.

Your role is to:
1. IMPLEMENT code based on detailed specifications
2. WRITE clean, readable, and maintainable code
3. FOLLOW Python best practices and PEP 8 standards
4. TEST your code using the available Python REPL tool
5. HANDLE edge cases and error conditions
6. CREATE comprehensive docstrings and comments

Code Quality Standards:
- Write clear, self-documenting code
- Use meaningful variable and function names
- Include proper error handling
- Add docstrings for all functions and classes
- Follow PEP 8 style guidelines
- Consider performance and efficiency
- Write modular, reusable code

When implementing code:
1. Start with a clear understanding of the requirements
2. Plan the code structure and approach
3. Implement step by step
4. Test each component as you build it
5. Debug and fix any issues
6. Provide clear explanations of your implementation

Testing Strategy:
- Test with typical inputs
- Test edge cases and boundary conditions
- Test error conditions
- Verify expected outputs
- Use the run_python_code tool to execute and verify your code

Always explain your code and testing approach. Be thorough but efficient."""
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Coder agent needs Python REPL and file tools"""
        from composio_openai import Action
        
        # Get file tools for code management
        file_tools = self.composio_toolset.get_tools(actions=[
            Action.FILETOOL_CREATE_FILE,
            Action.FILETOOL_EDIT_FILE,
            Action.FILETOOL_READ_FILE,
            Action.FILETOOL_LIST_FILES,
        ])
        
        # Add Python REPL tool
        python_repl = create_python_repl_tool()
        
        return [python_repl] + file_tools
    
    def implement_function(self, specification: str, function_name: str = None) -> str:
        """
        Implement a function based on the given specification.
        
        Args:
            specification: Detailed specification of what the function should do
            function_name: Optional specific function name to use
            
        Returns:
            Implementation result with code and testing
        """
        implementation_prompt = f"""
        Specification: {specification}
        Function Name: {function_name or 'Determine appropriate name'}
        
        Please implement this function following these steps:
        1. Analyze the specification thoroughly
        2. Design the function signature and structure
        3. Implement the function with proper error handling
        4. Add comprehensive docstring
        5. Test the function with various inputs
        6. Verify the implementation works correctly
        
        Use the run_python_code tool to test your implementation.
        """
        
        result = self.run(implementation_prompt)
        return result.content
    
    def implement_class(self, specification: str, class_name: str = None) -> str:
        """
        Implement a class based on the given specification.
        
        Args:
            specification: Detailed specification of the class
            class_name: Optional specific class name to use
            
        Returns:
            Implementation result with code and testing
        """
        implementation_prompt = f"""
        Specification: {specification}
        Class Name: {class_name or 'Determine appropriate name'}
        
        Please implement this class following these steps:
        1. Design the class structure and interface
        2. Implement the __init__ method
        3. Implement all required methods
        4. Add proper documentation
        5. Test the class functionality
        6. Verify all methods work correctly
        
        Use the run_python_code tool to test your implementation.
        """
        
        result = self.run(implementation_prompt)
        return result.content
    
    def fix_code(self, code: str, error_message: str) -> str:
        """
        Fix code based on an error message.
        
        Args:
            code: The code that has an error
            error_message: The error message to fix
            
        Returns:
            Fixed code with explanation
        """
        fix_prompt = f"""
        Code with error:
        ```python
        {code}
        ```
        
        Error message:
        {error_message}
        
        Please:
        1. Analyze the error and identify the root cause
        2. Fix the code to resolve the error
        3. Test the fixed code to ensure it works
        4. Explain what was wrong and how you fixed it
        
        Use the run_python_code tool to test your fixes.
        """
        
        result = self.run(fix_prompt)
        return result.content
    
    def optimize_code(self, code: str, optimization_goals: str = None) -> str:
        """
        Optimize existing code for better performance or readability.
        
        Args:
            code: The code to optimize
            optimization_goals: Specific optimization goals (performance, readability, etc.)
            
        Returns:
            Optimized code with explanation
        """
        optimization_prompt = f"""
        Code to optimize:
        ```python
        {code}
        ```
        
        Optimization Goals: {optimization_goals or 'General performance and readability'}
        
        Please:
        1. Analyze the current code for optimization opportunities
        2. Implement improvements while maintaining functionality
        3. Test the optimized code to ensure it still works correctly
        4. Explain the optimizations made and their benefits
        
        Use the run_python_code tool to verify your optimizations.
        """
        
        result = self.run(optimization_prompt)
        return result.content
    
    def create_module(self, specification: str, module_name: str = None) -> str:
        """
        Create a complete Python module based on specification.
        
        Args:
            specification: Detailed specification of the module
            module_name: Optional specific module name
            
        Returns:
            Complete module implementation
        """
        module_prompt = f"""
        Module Specification: {specification}
        Module Name: {module_name or 'Determine appropriate name'}
        
        Please create a complete Python module that includes:
        1. Module docstring explaining purpose and usage
        2. All necessary imports
        3. Constants and configuration (if needed)
        4. Function and class implementations
        5. Main execution block (if applicable)
        6. Comprehensive testing of all components
        
        Use the run_python_code tool to test each component.
        Create the module as a file using the file creation tools.
        """
        
        result = self.run(module_prompt)
        return result.content 