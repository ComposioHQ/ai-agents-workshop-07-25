#!/usr/bin/env python3
"""
Test script for the coding agent
This script runs a simple test to verify the agent is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_python_repl():
    """Test the Python REPL tool"""
    print("🧪 Testing Python REPL tool...")
    
    from coding_agent import run_python_code
    
    # Test basic execution
    result = run_python_code("print('Hello, World!')")
    print(f"REPL Test Result: {result}")
    
    # Test with variables
    result = run_python_code("x = 5\ny = 10\nprint(f'Sum: {x + y}')")
    print(f"REPL Test Result: {result}")
    
    # Test error handling
    result = run_python_code("print(undefined_variable)")
    print(f"REPL Error Test: {result}")
    
    return True

def test_agent_basic():
    """Test basic agent functionality"""
    print("🤖 Testing basic agent functionality...")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found. Please set up your .env file first.")
        return False
    
    try:
        from coding_agent import run_agent
        
        # Test with a simple request
        result = run_agent("Create a Python function that adds two numbers and test it with 3 and 5")
        
        print("✅ Agent test completed successfully!")
        print(f"Agent Response: {result[:200]}...")  # Show first 200 chars
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Coding Agent Tests")
    print("=" * 40)
    
    # Test 1: Python REPL
    try:
        test_python_repl()
        print("✅ Python REPL tests passed!")
    except Exception as e:
        print(f"❌ Python REPL tests failed: {str(e)}")
        return
    
    print("\n" + "=" * 40)
    
    # Test 2: Basic agent functionality
    if test_agent_basic():
        print("\n🎉 All tests passed! The coding agent is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check your setup.")

if __name__ == "__main__":
    main() 