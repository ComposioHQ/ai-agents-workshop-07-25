#!/usr/bin/env python3
"""
Examples for the Coding Agent - Toy Example

This script demonstrates various use cases for our simple coding agent.
Each example shows different capabilities and patterns.
"""

import os
import sys
from coding_agent import run_agent

# Add some colored output for better visibility
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_example_header(title, description):
    """Print a formatted header for each example"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}📚 Example: {title}{Colors.END}")
    print(f"{Colors.YELLOW}{description}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def run_example(title, description, request):
    """Run a single example with proper formatting"""
    print_example_header(title, description)
    
    try:
        result = run_agent(request)
        print(f"\n{Colors.GREEN}✅ Example completed successfully!{Colors.END}")
        return True
    except Exception as e:
        print(f"\n{Colors.RED}❌ Example failed: {str(e)}{Colors.END}")
        return False

def main():
    """Run all examples"""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Colors.RED}❌ Error: OPENAI_API_KEY environment variable is required{Colors.END}")
        print("Please set it in your .env file or environment")
        return
    
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 Coding Agent Examples{Colors.END}")
    print("This script demonstrates various capabilities of our toy coding agent.")
    print("Each example will show different patterns and use cases.\n")
    
    # Example 1: Basic function creation and testing
    success1 = run_example(
        "Basic Function Creation",
        "Create a simple function and test it",
        "Create a Python function that checks if a number is prime and test it on the number 7"
    )
    
    if not success1:
        print(f"{Colors.RED}Stopping examples due to error.{Colors.END}")
        return
    
    # Example 2: Math operations
    run_example(
        "Mathematical Functions",
        "Create a function for mathematical calculations",
        "Create a Python function that calculates the factorial of a number and test it with the number 5"
    )
    
    # Example 3: String manipulation
    run_example(
        "String Processing",
        "Work with text and string operations",
        "Create a Python function that counts the number of vowels in a string and test it with the phrase 'Hello World'"
    )
    
    # Example 4: Data structures
    run_example(
        "Data Structure Operations",
        "Work with lists and data manipulation",
        "Create a Python function that finds the second largest number in a list and test it with [3, 1, 4, 1, 5, 9, 2, 6]"
    )
    
    # Example 5: File operations
    run_example(
        "File Operations",
        "Create files and work with file system",
        "Create a Python function that generates a list of even numbers from 1 to 20 and save it to a file called 'even_numbers.txt'"
    )
    
    # Example 6: Error handling
    run_example(
        "Error Handling",
        "Demonstrate robust error handling",
        "Create a Python function that safely divides two numbers and handles division by zero, then test it with various inputs including 10/2 and 10/0"
    )
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All examples completed!{Colors.END}")
    print(f"{Colors.BLUE}Check the files created in the current directory.{Colors.END}")

if __name__ == "__main__":
    main() 