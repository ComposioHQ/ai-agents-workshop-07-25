#!/usr/bin/env python3
"""
Multi-Agent System Examples

This script demonstrates various use cases and workflows for the multi-agent system,
showcasing different patterns of agent collaboration and specialization.
"""

import os
import sys
from multi_agent_system import MultiAgentSystem, Colors

def print_example_header(title: str, description: str):
    """Print formatted header for each example"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}📚 Example: {title}{Colors.END}")
    print(f"{Colors.YELLOW}{description}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")

def run_example(title: str, description: str, task: str, requirements: dict = None):
    """Run a single example with proper formatting"""
    print_example_header(title, description)
    
    system = MultiAgentSystem()
    
    try:
        result = system.run_complete_workflow(task, requirements)
        
        if result.success:
            print(f"\n{Colors.GREEN}✅ Example completed successfully!{Colors.END}")
            print(f"{Colors.GREEN}⏱️  Execution time: {result.execution_time:.2f} seconds{Colors.END}")
            print(f"{Colors.GREEN}💰 Estimated cost: ${result.total_cost_estimate:.4f}{Colors.END}")
            
            # Show model usage
            print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Model Usage:{Colors.END}")
            for agent_name, artifact in result.artifacts.items():
                model_used = artifact.get('model_used', 'unknown')
                print(f"  {agent_name.title()}: {model_used}")
        else:
            print(f"\n{Colors.RED}❌ Example failed: {result.final_output}{Colors.END}")
            
        return result.success
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Example failed with error: {str(e)}{Colors.END}")
        return False

def demonstrate_handoff_pattern():
    """Demonstrate the agent handoff pattern"""
    print_example_header(
        "Agent Handoff Pattern", 
        "Shows how agents can hand off tasks to each other for specialized processing"
    )
    
    system = MultiAgentSystem()
    
    result = system.demonstrate_handoff("Create a function to calculate Fibonacci numbers")
    
    print(f"\n{Colors.GREEN}✅ Handoff demonstration completed{Colors.END}")
    print(f"\n{Colors.BOLD}{Colors.BLUE}📄 Results Summary:{Colors.END}")
    print(f"Plan length: {len(result['plan'])} characters")
    print(f"Code length: {len(result['code'])} characters")
    print(f"Review length: {len(result['review'])} characters")

def demonstrate_cost_optimization():
    """Demonstrate cost optimization through model selection"""
    print_example_header(
        "Cost Optimization",
        "Shows how different agents use different models for cost efficiency"
    )
    
    system = MultiAgentSystem()
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}🤖 Agent Model Configuration:{Colors.END}")
    agent_info = system.get_agent_info()
    
    for name, info in agent_info.items():
        model = info['model']
        cost_per_1k = system.model_costs.get(model, 0.01)
        print(f"  {name.title()}: {model} (${cost_per_1k:.4f}/1K tokens)")
    
    print(f"\n{Colors.YELLOW}📊 Cost Optimization Strategy:{Colors.END}")
    print(f"  • Planner & Coder: GPT-4 for complex reasoning and code generation")
    print(f"  • Reviewer & Tester: GPT-3.5-turbo for structured tasks")
    print(f"  • Estimated savings: ~60-70% compared to using GPT-4 for all tasks")

def main():
    """Run all examples"""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Colors.RED}❌ Error: OPENAI_API_KEY environment variable is required{Colors.END}")
        print("Please set it in your .env file or environment")
        return
    
    print(f"{Colors.BOLD}{Colors.CYAN}🚀 Multi-Agent System Examples{Colors.END}")
    print("This script demonstrates various multi-agent workflows and patterns.")
    print("Each example shows different aspects of agent collaboration and specialization.")
    
    # Example 1: Simple Algorithm Implementation
    success1 = run_example(
        "Simple Algorithm Implementation",
        "Basic workflow: Plan → Code → Review → Test",
        "Create a Python function that implements the bubble sort algorithm"
    )
    
    if not success1:
        print(f"{Colors.RED}Stopping examples due to error in first example.{Colors.END}")
        return
    
    # Example 2: Data Structure Implementation
    run_example(
        "Data Structure Implementation",
        "More complex task requiring careful design and testing",
        "Create a Python class that implements a binary search tree with insert, search, and delete operations"
    )
    
    # Example 3: Algorithm with Requirements
    run_example(
        "Algorithm with Specific Requirements",
        "Demonstrates how agents handle detailed requirements",
        "Create a Python function that finds the shortest path in a graph",
        requirements={
            "algorithm": "Dijkstra's algorithm",
            "input_format": "adjacency list",
            "return_format": "list of nodes representing path",
            "handle_disconnected": True,
            "performance": "O(V log V + E) complexity"
        }
    )
    
    # Example 4: Utility Function
    run_example(
        "Utility Function Creation",
        "Shows agents working on practical programming tasks",
        "Create a Python function that validates email addresses using regex and handles edge cases"
    )
    
    # Example 5: File Processing
    run_example(
        "File Processing Function",
        "Demonstrates agents handling I/O operations and error handling",
        "Create a Python function that reads a CSV file, processes the data, and writes results to a new file"
    )
    
    # Demonstrate handoff pattern
    demonstrate_handoff_pattern()
    
    # Demonstrate cost optimization
    demonstrate_cost_optimization()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All examples completed!{Colors.END}")
    print(f"{Colors.BLUE}Key takeaways:{Colors.END}")
    print(f"  • Agent specialization improves quality and efficiency")
    print(f"  • Model selection enables significant cost optimization")
    print(f"  • Handoff mechanisms enable seamless collaboration")
    print(f"  • Workflow orchestration ensures consistent results")

if __name__ == "__main__":
    main() 