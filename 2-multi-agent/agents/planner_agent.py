"""
Planner Agent

This agent specializes in breaking down tasks into manageable steps
and creating detailed implementation plans. It uses GPT-4 for strategic thinking.
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent
from ..utils.python_repl import create_python_repl_tool


class PlannerAgent(BaseAgent):
    """
    Agent that specializes in planning and task decomposition.
    
    This agent:
    - Analyzes complex requirements
    - Breaks down tasks into manageable steps
    - Creates detailed implementation plans
    - Suggests optimal approaches and architectures
    """
    
    def __init__(self, **kwargs):
        # Use GPT-4 for strategic planning (default)
        kwargs.setdefault('model', 'gpt-4')
        kwargs.setdefault('name', 'Planner')
        kwargs.setdefault('temperature', 0.3)  # Lower temperature for more structured planning
        
        super().__init__(**kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are a Planner Agent, specialized in breaking down complex coding tasks into manageable steps.

Your role is to:
1. ANALYZE the given requirements thoroughly
2. BREAK DOWN the task into logical, sequential steps
3. CREATE detailed implementation plans
4. SUGGEST optimal approaches and design patterns
5. IDENTIFY potential challenges and solutions
6. PROVIDE clear specifications for other agents

Guidelines:
- Think step-by-step and be methodical
- Consider edge cases and error handling
- Suggest appropriate data structures and algorithms
- Provide clear acceptance criteria for each step
- Estimate complexity and effort for each component
- Consider code quality, maintainability, and performance

When creating a plan:
1. Start with a high-level overview
2. Break down into specific, actionable steps
3. Define inputs and outputs for each step
4. Identify dependencies between steps
5. Suggest testing strategies

Format your response as a structured plan with:
- Executive Summary
- Step-by-step breakdown
- Technical specifications
- Potential challenges and solutions
- Testing recommendations

Be thorough but concise. Your plan will guide other specialized agents."""
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Planner agent doesn't need code execution tools, but can use file tools for documentation"""
        from composio_openai import Action
        
        # Get basic file tools for creating documentation
        file_tools = self.composio_toolset.get_tools(actions=[
            Action.FILETOOL_CREATE_FILE,
            Action.FILETOOL_READ_FILE,
            Action.FILETOOL_LIST_FILES,
        ])
        
        return file_tools
    
    def create_implementation_plan(self, task: str, requirements: Dict[str, Any] = None) -> str:
        """
        Create a detailed implementation plan for a given task.
        
        Args:
            task: The main task to plan for
            requirements: Optional specific requirements or constraints
            
        Returns:
            Detailed implementation plan
        """
        planning_prompt = f"""
        Task: {task}
        
        Additional Requirements: {requirements or 'None specified'}
        
        Create a comprehensive implementation plan that includes:
        1. Analysis of the requirements
        2. High-level architecture and approach
        3. Detailed step-by-step implementation plan
        4. Technical specifications for each component
        5. Testing strategy and acceptance criteria
        6. Risk assessment and mitigation strategies
        
        Be specific about what each step should accomplish and how it connects to other steps.
        """
        
        result = self.run(planning_prompt)
        return result.content
    
    def suggest_agent_workflow(self, task: str) -> Dict[str, Any]:
        """
        Suggest which agents should be involved and in what order.
        
        Args:
            task: The task to analyze
            
        Returns:
            Dictionary containing suggested workflow
        """
        workflow_prompt = f"""
        Task: {task}
        
        Available agents:
        - Planner: Creates implementation plans (you)
        - Coder: Writes Python code based on specifications
        - Reviewer: Reviews code for bugs, style, and improvements
        - Tester: Creates and runs tests for code validation
        
        Suggest an optimal workflow that specifies:
        1. Which agents should be involved
        2. In what order they should work
        3. What each agent should focus on
        4. How the agents should collaborate
        5. What handoff criteria should be used
        
        Format as a structured workflow plan.
        """
        
        result = self.run(workflow_prompt)
        return {
            "workflow_plan": result.content,
            "success": result.success
        }
    
    def estimate_complexity(self, task: str) -> Dict[str, Any]:
        """
        Estimate the complexity and effort required for a task.
        
        Args:
            task: The task to analyze
            
        Returns:
            Dictionary containing complexity analysis
        """
        complexity_prompt = f"""
        Task: {task}
        
        Provide a complexity analysis including:
        1. Overall complexity rating (Simple/Medium/Complex/Expert)
        2. Estimated implementation time
        3. Key technical challenges
        4. Required skills and knowledge
        5. Dependencies and prerequisites
        6. Risk factors
        
        Be specific about what makes this task complex or simple.
        """
        
        result = self.run(complexity_prompt)
        return {
            "complexity_analysis": result.content,
            "success": result.success
        } 