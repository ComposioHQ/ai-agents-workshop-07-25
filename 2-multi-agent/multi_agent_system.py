#!/usr/bin/env python3
"""
Multi-Agent System Orchestrator

This module provides the main orchestration system that coordinates
specialized agents to work together on complex coding tasks.

Features:
- Agent coordination and handoff mechanisms
- Cost optimization through appropriate model selection
- Task decomposition and workflow management
- Real-time progress tracking and reporting
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agents
from agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent, BaseAgent

# Colored output for better visualization
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'


@dataclass
class WorkflowStep:
    """Represents a step in the multi-agent workflow"""
    agent_name: str
    task: str
    depends_on: Optional[List[str]] = None
    completed: bool = False
    result: Optional[Any] = None
    cost_estimate: Optional[float] = None


@dataclass
class AgentWorkflowResult:
    """Represents the complete result of a multi-agent workflow"""
    success: bool
    workflow_steps: List[WorkflowStep]
    total_cost_estimate: float
    execution_time: float
    final_output: str
    artifacts: Dict[str, Any]


class MultiAgentSystem:
    """
    Main orchestrator for the multi-agent system.
    
    This class coordinates multiple specialized agents to work together
    on complex coding tasks, demonstrating:
    - Agent specialization and separation of concerns
    - Cost optimization through model selection
    - Handoff mechanisms between agents
    - Workflow management and coordination
    """
    
    def __init__(self):
        # Initialize all agents with their specialized configurations
        self.agents = {
            'planner': PlannerAgent(model='gpt-4', temperature=0.3),
            'coder': CoderAgent(model='gpt-4', temperature=0.1),
            'reviewer': ReviewerAgent(model='gpt-3.5-turbo', temperature=0.2),
            'tester': TesterAgent(model='gpt-3.5-turbo', temperature=0.1)
        }
        
        # Cost tracking (approximate costs per 1K tokens)
        self.model_costs = {
            'gpt-4': 0.03,  # $0.03 per 1K tokens
            'gpt-3.5-turbo': 0.002,  # $0.002 per 1K tokens
        }
        
        # Workflow tracking
        self.current_workflow: Optional[List[WorkflowStep]] = None
        self.workflow_context: Dict[str, Any] = {}
    
    def print_agent_action(self, agent_name: str, action: str, details: str = ""):
        """Print formatted agent action"""
        agent_colors = {
            'planner': Colors.BLUE,
            'coder': Colors.GREEN,
            'reviewer': Colors.YELLOW,
            'tester': Colors.PURPLE
        }
        
        color = agent_colors.get(agent_name.lower(), Colors.WHITE)
        print(f"{color}🤖 {agent_name.title()} Agent{Colors.END}: {action}")
        if details:
            print(f"   {details}")
    
    def estimate_cost(self, agent_name: str, task_complexity: str = "medium") -> float:
        """Estimate the cost for a task based on agent and complexity"""
        agent = self.agents[agent_name]
        base_cost = self.model_costs.get(agent.model, 0.01)
        
        complexity_multipliers = {
            "simple": 0.5,
            "medium": 1.0,
            "complex": 2.0,
            "expert": 3.0
        }
        
        return base_cost * complexity_multipliers.get(task_complexity, 1.0)
    
    def create_workflow(self, task: str, requirements: Dict[str, Any] = None) -> List[WorkflowStep]:
        """
        Create an optimal workflow for the given task.
        
        Args:
            task: The main task to accomplish
            requirements: Optional specific requirements
            
        Returns:
            List of workflow steps
        """
        self.print_agent_action("planner", "Creating workflow plan", f"Task: {task}")
        
        # Get workflow suggestion from planner
        workflow_result = self.agents['planner'].suggest_agent_workflow(task)
        
        # Create standard workflow steps
        workflow_steps = [
            WorkflowStep(
                agent_name="planner",
                task=f"Create implementation plan for: {task}",
                cost_estimate=self.estimate_cost("planner", "medium")
            ),
            WorkflowStep(
                agent_name="coder",
                task=f"Implement code based on plan: {task}",
                depends_on=["planner"],
                cost_estimate=self.estimate_cost("coder", "complex")
            ),
            WorkflowStep(
                agent_name="reviewer",
                task="Review code for quality, bugs, and improvements",
                depends_on=["coder"],
                cost_estimate=self.estimate_cost("reviewer", "medium")
            ),
            WorkflowStep(
                agent_name="tester",
                task="Create and run comprehensive tests",
                depends_on=["coder"],
                cost_estimate=self.estimate_cost("tester", "medium")
            )
        ]
        
        # Store workflow context
        self.workflow_context = {
            "original_task": task,
            "requirements": requirements or {},
            "workflow_plan": workflow_result
        }
        
        return workflow_steps
    
    def execute_workflow_step(self, step: WorkflowStep) -> Any:
        """Execute a single workflow step"""
        self.print_agent_action(step.agent_name, f"Executing step", step.task)
        
        agent = self.agents[step.agent_name]
        
        # Add context from previous steps
        context = self.workflow_context.copy()
        if step.depends_on:
            for dep in step.depends_on:
                dep_step = next((s for s in self.current_workflow if s.agent_name == dep), None)
                if dep_step and dep_step.completed:
                    context[f"{dep}_result"] = dep_step.result
        
        # Execute the step
        result = agent.run(step.task, context)
        
        # Update step
        step.completed = True
        step.result = result
        
        # Update workflow context
        self.workflow_context[f"{step.agent_name}_result"] = result
        
        return result
    
    def run_complete_workflow(self, task: str, requirements: Dict[str, Any] = None) -> AgentWorkflowResult:
        """
        Run a complete multi-agent workflow for the given task.
        
        Args:
            task: The main task to accomplish
            requirements: Optional specific requirements
            
        Returns:
            Complete workflow result
        """
        start_time = datetime.now()
        
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 Starting Multi-Agent Workflow{Colors.END}")
        print(f"{Colors.CYAN}Task: {task}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        try:
            # Create workflow
            workflow_steps = self.create_workflow(task, requirements)
            self.current_workflow = workflow_steps
            
            # Calculate total estimated cost
            total_cost = sum(step.cost_estimate or 0 for step in workflow_steps)
            print(f"{Colors.YELLOW}💰 Estimated cost: ${total_cost:.4f}{Colors.END}")
            
            # Execute workflow steps
            artifacts = {}
            
            for step in workflow_steps:
                if step.depends_on:
                    # Check if dependencies are completed
                    for dep in step.depends_on:
                        dep_step = next((s for s in workflow_steps if s.agent_name == dep), None)
                        if not dep_step or not dep_step.completed:
                            print(f"{Colors.RED}❌ Dependency {dep} not completed{Colors.END}")
                            continue
                
                # Execute step
                result = self.execute_workflow_step(step)
                
                # Store artifacts
                artifacts[step.agent_name] = {
                    "task": step.task,
                    "result": result.content if hasattr(result, 'content') else str(result),
                    "success": result.success if hasattr(result, 'success') else True,
                    "model_used": result.model_used if hasattr(result, 'model_used') else step.agent_name
                }
                
                print(f"{Colors.GREEN}✅ Completed: {step.agent_name}{Colors.END}")
            
            # Generate final output
            final_output = self._generate_final_output(artifacts)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"{Colors.CYAN}{'='*60}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.GREEN}🎉 Workflow completed successfully!{Colors.END}")
            print(f"{Colors.GREEN}⏱️  Execution time: {execution_time:.2f} seconds{Colors.END}")
            print(f"{Colors.GREEN}💰 Estimated cost: ${total_cost:.4f}{Colors.END}")
            
            return AgentWorkflowResult(
                success=True,
                workflow_steps=workflow_steps,
                total_cost_estimate=total_cost,
                execution_time=execution_time,
                final_output=final_output,
                artifacts=artifacts
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            print(f"{Colors.RED}❌ Workflow failed: {str(e)}{Colors.END}")
            
            return AgentWorkflowResult(
                success=False,
                workflow_steps=self.current_workflow or [],
                total_cost_estimate=0.0,
                execution_time=execution_time,
                final_output=f"Workflow failed: {str(e)}",
                artifacts={}
            )
    
    def _generate_final_output(self, artifacts: Dict[str, Any]) -> str:
        """Generate a comprehensive final output from all artifacts"""
        output = []
        
        output.append("# Multi-Agent Workflow Results")
        output.append("="*50)
        
        # Add planner results
        if 'planner' in artifacts:
            output.append("\n## 📋 Implementation Plan")
            output.append(artifacts['planner']['result'])
        
        # Add coder results
        if 'coder' in artifacts:
            output.append("\n## 💻 Code Implementation")
            output.append(artifacts['coder']['result'])
        
        # Add reviewer results
        if 'reviewer' in artifacts:
            output.append("\n## 🔍 Code Review")
            output.append(artifacts['reviewer']['result'])
        
        # Add tester results
        if 'tester' in artifacts:
            output.append("\n## 🧪 Test Results")
            output.append(artifacts['tester']['result'])
        
        # Add model usage summary
        output.append("\n## 📊 Model Usage & Cost Optimization")
        for agent_name, artifact in artifacts.items():
            model_used = artifact.get('model_used', 'unknown')
            output.append(f"- {agent_name.title()}: {model_used}")
        
        return "\n".join(output)
    
    def demonstrate_handoff(self, task: str):
        """Demonstrate agent handoff mechanism"""
        print(f"{Colors.BOLD}{Colors.CYAN}🔄 Demonstrating Agent Handoff{Colors.END}")
        print(f"{Colors.CYAN}Task: {task}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        # Start with planner
        planner = self.agents['planner']
        self.print_agent_action("planner", "Creating plan")
        plan_result = planner.run(f"Create a plan for: {task}")
        
        # Hand off to coder
        coder = self.agents['coder']
        self.print_agent_action("planner", "Handing off to coder")
        code_result = planner.handoff_to(coder, f"Implement based on plan: {task}")
        
        # Hand off to reviewer
        reviewer = self.agents['reviewer']
        self.print_agent_action("coder", "Handing off to reviewer")
        review_result = coder.handoff_to(reviewer, "Review the implemented code")
        
        print(f"{Colors.GREEN}✅ Handoff demonstration completed{Colors.END}")
        
        return {
            "plan": plan_result.content,
            "code": code_result.content,
            "review": review_result.content
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all agents"""
        return {
            name: agent.get_info() 
            for name, agent in self.agents.items()
        }


def main():
    """Main function to run the multi-agent system"""
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Colors.RED}❌ Error: OPENAI_API_KEY environment variable is required{Colors.END}")
        print("Please set it in your .env file or environment")
        return
    
    # Get task from command line or use default
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Create a Python function that implements a binary search algorithm"
    
    # Initialize and run the multi-agent system
    system = MultiAgentSystem()
    
    # Run complete workflow
    result = system.run_complete_workflow(task)
    
    # Print final output
    print(f"\n{Colors.BOLD}{Colors.BLUE}📄 Final Output:{Colors.END}")
    print(result.final_output)
    
    # Print agent information
    print(f"\n{Colors.BOLD}{Colors.CYAN}🤖 Agent Information:{Colors.END}")
    agent_info = system.get_agent_info()
    for name, info in agent_info.items():
        print(f"  {name.title()}: {info['model']} (messages: {info['message_count']})")


if __name__ == "__main__":
    main() 