#!/usr/bin/env python3
"""
Interactive Multi-Agent System Demo

This script allows users to interact with the multi-agent system
and see how different agents collaborate to solve coding tasks.
"""

import asyncio
import os
from dotenv import load_dotenv
from multi_agent_system import run_multi_agent_system

# Load environment variables
load_dotenv()

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print the application header"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🤖 Multi-Agent Software Development System")
    print("=" * 60)
    print("This system uses specialized AI agents to:")
    print("• 📋 Plan your software requirements")
    print("• 💻 Implement the code")
    print("• 🔍 Review and test the implementation")
    print("=" * 60)
    print(f"{Colors.ENDC}")

def print_examples():
    """Print example requests users can try"""
    print(f"{Colors.OKBLUE}💡 Example Requests You Can Try:{Colors.ENDC}")
    print()
    
    examples = [
        "Create a password generator with different complexity levels",
        "Build a file organizer that sorts files by type and date",
        "Make a simple web scraper for extracting article titles",
        "Create a CSV data analyzer with visualization",
        "Build a text-based adventure game",
        "Create a URL shortener with analytics",
        "Make a simple expense tracker",
        "Build a markdown to HTML converter",
        "Create a file backup utility",
        "Make a simple chat bot using pattern matching"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{Colors.OKCYAN}{i:2d}.{Colors.ENDC} {example}")
    
    print()

def print_agent_info():
    """Print information about the agents"""
    print(f"{Colors.OKGREEN}🤖 Meet Your Development Team:{Colors.ENDC}")
    print()
    
    agents = [
        ("Triage", "🎯", "Orchestrates the workflow and routes tasks", "gpt-4.1-mini"),
        ("Planner", "📋", "Breaks down requirements into actionable tasks", "gpt-4.1-mini"),
        ("Coder", "💻", "Implements the actual code with testing", "gpt-4.1"),
        ("Reviewer", "🔍", "Reviews code quality and validates implementation", "gpt-4.1-mini"),
    ]
    
    for name, icon, description, model in agents:
        print(f"{Colors.BOLD}{icon} {name}{Colors.ENDC}")
        print(f"   Role: {description}")
        print(f"   Model: {model} {'(💰 cost-optimized)' if 'mini' in model else '(🚀 powerful)'}")
        print()

async def interactive_session():
    """Run interactive session with user"""
    print_header()
    print_agent_info()
    print_examples()
    
    session_count = 0
    
    while True:
        session_count += 1
        
        print(f"{Colors.HEADER}Session {session_count}{Colors.ENDC}")
        print("=" * 40)
        
        # Get user input
        print(f"{Colors.OKBLUE}Enter your software development request:{Colors.ENDC}")
        print("(Type 'quit' to exit, 'examples' to see examples again)")
        print()
        
        user_input = input(f"{Colors.BOLD}> {Colors.ENDC}").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"{Colors.OKGREEN}Thanks for using the Multi-Agent System! 👋{Colors.ENDC}")
            break
        
        if user_input.lower() in ['examples', 'help', 'h']:
            print_examples()
            continue
        
        if not user_input:
            print(f"{Colors.WARNING}Please enter a request.{Colors.ENDC}")
            continue
        
        # Get project name
        project_name = input(f"{Colors.OKBLUE}Project name (optional): {Colors.ENDC}").strip()
        if not project_name:
            project_name = f"Project{session_count}"
        
        print(f"\n{Colors.OKGREEN}🚀 Starting development process...{Colors.ENDC}")
        print(f"Request: {user_input}")
        print(f"Project: {project_name}")
        print()
        
        try:
            # Run the multi-agent system
            result = await run_multi_agent_system(user_input, project_name)
            
            print(f"\n{Colors.OKGREEN}✅ Development Complete!{Colors.ENDC}")
            print("=" * 50)
            print(f"{Colors.BOLD}Final Result:{Colors.ENDC}")
            print(result)
            print("=" * 50)
            
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
            print("Please check your API key and try again.")
        
        print(f"\n{Colors.OKCYAN}Ready for your next request!{Colors.ENDC}")
        print()

async def quick_demo():
    """Run a quick demo without user input"""
    print_header()
    print(f"{Colors.OKGREEN}🎯 Quick Demo: Creating a Simple Calculator{Colors.ENDC}")
    print()
    
    request = """
    Create a simple calculator that can:
    1. Perform basic arithmetic operations (+, -, *, /)
    2. Handle decimal numbers
    3. Include error handling for invalid inputs
    4. Have a clean command-line interface
    """
    
    try:
        result = await run_multi_agent_system(request, "CalculatorDemo")
        print(f"\n{Colors.OKGREEN}✅ Demo Complete!{Colors.ENDC}")
        print("=" * 50)
        print(result)
        print("=" * 50)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Demo failed: {str(e)}{Colors.ENDC}")

async def main():
    """Main function"""
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Colors.FAIL}❌ Error: OPENAI_API_KEY environment variable is required{Colors.ENDC}")
        print("Please set it in your .env file or environment")
        return
    
    print(f"{Colors.OKBLUE}Choose an option:{Colors.ENDC}")
    print("1. Interactive session (recommended)")
    print("2. Quick demo")
    print("3. Exit")
    
    choice = input(f"{Colors.BOLD}Enter your choice (1-3): {Colors.ENDC}").strip()
    
    if choice == "1":
        await interactive_session()
    elif choice == "2":
        await quick_demo()
    elif choice == "3":
        print(f"{Colors.OKGREEN}Goodbye! 👋{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}Invalid choice. Please run the script again.{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main()) 