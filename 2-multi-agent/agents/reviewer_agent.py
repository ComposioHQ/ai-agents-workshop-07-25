"""
Reviewer Agent

This agent specializes in reviewing code for bugs, style issues, and improvements.
It uses GPT-3.5-turbo for cost optimization since code review is a more structured task.
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent
from ..utils.python_repl import create_python_repl_tool


class ReviewerAgent(BaseAgent):
    """
    Agent that specializes in code review and quality assurance.
    
    This agent:
    - Reviews code for bugs and logical errors
    - Checks code style and adherence to best practices
    - Suggests improvements and optimizations
    - Validates code against requirements
    - Provides constructive feedback
    
    Uses GPT-3.5-turbo for cost optimization.
    """
    
    def __init__(self, **kwargs):
        # Use GPT-3.5-turbo for cost-effective code review
        kwargs.setdefault('model', 'gpt-3.5-turbo')
        kwargs.setdefault('name', 'Reviewer')
        kwargs.setdefault('temperature', 0.2)  # Lower temperature for consistent reviews
        
        super().__init__(**kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are a Reviewer Agent, specialized in code review and quality assurance.

Your role is to:
1. REVIEW code for bugs, logical errors, and edge cases
2. CHECK code style and adherence to Python best practices
3. SUGGEST improvements for readability and maintainability
4. VALIDATE that code meets the specified requirements
5. PROVIDE constructive, actionable feedback
6. IDENTIFY potential security issues or performance problems

Review Categories:
1. FUNCTIONALITY: Does the code work as intended?
2. STYLE: Does it follow PEP 8 and Python conventions?
3. READABILITY: Is the code clear and well-documented?
4. EFFICIENCY: Are there performance improvements possible?
5. ROBUSTNESS: Does it handle edge cases and errors properly?
6. SECURITY: Are there potential security vulnerabilities?

Review Process:
1. Read and understand the code thoroughly
2. Check for logical errors and bugs
3. Verify adherence to coding standards
4. Suggest specific improvements
5. Test critical parts if necessary
6. Provide clear, actionable feedback

Feedback Format:
- Start with overall assessment
- List specific issues found
- Provide concrete suggestions for improvement
- Explain the reasoning behind each suggestion
- Prioritize issues by severity (Critical, High, Medium, Low)

Be thorough but constructive. Focus on helping improve code quality."""
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Reviewer agent needs Python REPL for testing and file tools for reading code"""
        from composio_openai import Action
        
        # Get file tools for reading and analyzing code
        file_tools = self.composio_toolset.get_tools(actions=[
            Action.FILETOOL_READ_FILE,
            Action.FILETOOL_LIST_FILES,
        ])
        
        # Add Python REPL tool for testing code during review
        python_repl = create_python_repl_tool()
        
        return [python_repl] + file_tools
    
    def review_code(self, code: str, requirements: str = None) -> Dict[str, Any]:
        """
        Perform a comprehensive code review.
        
        Args:
            code: The code to review
            requirements: Optional requirements to validate against
            
        Returns:
            Dictionary containing review results
        """
        review_prompt = f"""
        Code to review:
        ```python
        {code}
        ```
        
        Requirements: {requirements or 'None specified'}
        
        Please perform a comprehensive code review including:
        
        1. FUNCTIONALITY REVIEW:
           - Does the code work as intended?
           - Are there any logical errors?
           - Does it handle edge cases properly?
           - Test critical functionality if needed
        
        2. STYLE REVIEW:
           - PEP 8 compliance
           - Naming conventions
           - Code structure and organization
           - Documentation quality
        
        3. QUALITY ASSESSMENT:
           - Code readability and maintainability
           - Error handling
           - Performance considerations
           - Security implications
        
        4. IMPROVEMENT SUGGESTIONS:
           - Specific recommendations
           - Code examples where helpful
           - Priority levels for each issue
        
        Use the run_python_code tool to test any suspicious code sections.
        """
        
        result = self.run(review_prompt)
        return {
            "review_content": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def quick_style_check(self, code: str) -> Dict[str, Any]:
        """
        Perform a quick style and formatting check.
        
        Args:
            code: The code to check
            
        Returns:
            Dictionary containing style check results
        """
        style_prompt = f"""
        Code to check for style issues:
        ```python
        {code}
        ```
        
        Perform a focused style review checking:
        1. PEP 8 compliance
        2. Naming conventions
        3. Docstring presence and quality
        4. Code formatting and structure
        5. Import organization
        
        Provide a concise list of style issues with specific line references and suggestions.
        """
        
        result = self.run(style_prompt)
        return {
            "style_issues": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def security_review(self, code: str) -> Dict[str, Any]:
        """
        Perform a security-focused code review.
        
        Args:
            code: The code to review for security issues
            
        Returns:
            Dictionary containing security review results
        """
        security_prompt = f"""
        Code to review for security issues:
        ```python
        {code}
        ```
        
        Perform a security-focused review checking for:
        1. Input validation and sanitization
        2. Potential injection vulnerabilities
        3. Unsafe use of eval() or exec()
        4. File system access security
        5. Authentication and authorization issues
        6. Error handling that might leak information
        7. Use of deprecated or insecure functions
        
        Identify specific security concerns and provide recommendations.
        """
        
        result = self.run(security_prompt)
        return {
            "security_issues": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def performance_review(self, code: str) -> Dict[str, Any]:
        """
        Perform a performance-focused code review.
        
        Args:
            code: The code to review for performance issues
            
        Returns:
            Dictionary containing performance review results
        """
        performance_prompt = f"""
        Code to review for performance issues:
        ```python
        {code}
        ```
        
        Perform a performance-focused review checking for:
        1. Algorithmic complexity issues
        2. Inefficient data structures
        3. Unnecessary loops or computations
        4. Memory usage concerns
        5. I/O operation optimization
        6. Database query efficiency (if applicable)
        
        Suggest specific optimizations with explanations.
        """
        
        result = self.run(performance_prompt)
        return {
            "performance_issues": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def compare_implementations(self, code1: str, code2: str, criteria: str = None) -> Dict[str, Any]:
        """
        Compare two code implementations and provide analysis.
        
        Args:
            code1: First implementation
            code2: Second implementation
            criteria: Optional specific criteria to focus on
            
        Returns:
            Dictionary containing comparison results
        """
        comparison_prompt = f"""
        Compare these two implementations:
        
        Implementation 1:
        ```python
        {code1}
        ```
        
        Implementation 2:
        ```python
        {code2}
        ```
        
        Comparison Criteria: {criteria or 'General quality, performance, and readability'}
        
        Provide a detailed comparison including:
        1. Functional differences
        2. Performance comparison
        3. Readability and maintainability
        4. Pros and cons of each approach
        5. Recommendation with reasoning
        
        Test both implementations if necessary to verify functionality.
        """
        
        result = self.run(comparison_prompt)
        return {
            "comparison_analysis": result.content,
            "success": result.success,
            "model_used": self.model
        } 