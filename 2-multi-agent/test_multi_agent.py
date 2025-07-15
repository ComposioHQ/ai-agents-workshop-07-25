#!/usr/bin/env python3
"""
Test script for Multi-Agent System

This script tests the multi-agent system functionality
to ensure everything is working correctly.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_from_scratch_agent():
    """Test the from-scratch agent implementation"""
    print("🧪 Testing From-Scratch Agent Implementation")
    print("=" * 50)
    
    try:
        from agent_from_scratch import BasicAgent, calculate, get_current_time
        
        # Create agent
        agent = BasicAgent(
            name="Test Agent",
            instructions="You are a helpful test agent.",
            tools=[calculate, get_current_time],
            model="gpt-4.1-mini"
        )
        
        print("✅ Agent created successfully")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Tools: {len(agent.tools)}")
        
        # Test tool execution
        print("\n🔧 Testing tool execution...")
        
        # Test simple request
        response = agent.run("What is 5 + 3?")
        print(f"✅ Agent response: {response[:100]}...")
        
        # Reset for next test
        agent.reset_conversation()
        
        return True
        
    except Exception as e:
        print(f"❌ From-scratch agent test failed: {str(e)}")
        return False

async def test_multi_agent_system():
    """Test the multi-agent system"""
    print("\n🤖 Testing Multi-Agent System")
    print("=" * 50)
    
    try:
        from multi_agent_system import run_multi_agent_system
        
        # Test simple request
        request = "Create a simple function that adds two numbers together and test it."
        print(f"Request: {request}")
        
        result = await run_multi_agent_system(request, "TestProject")
        
        if result and "error" not in result.lower():
            print("✅ Multi-agent system test passed")
            print(f"   Response length: {len(result)} characters")
            return True
        else:
            print(f"❌ Multi-agent system test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-agent system test failed: {str(e)}")
        return False

def test_environment():
    """Test environment setup"""
    print("🌍 Testing Environment Setup")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not found")
        return False
    elif len(api_key) < 10:
        print("❌ OPENAI_API_KEY appears to be invalid")
        return False
    else:
        print("✅ OPENAI_API_KEY is set")
    
    # Check required packages
    required_packages = [
        "openai",
        "composio_openai",
        "python-dotenv",
        "pydantic",
        "asyncio"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def print_test_summary(results):
    """Print test summary"""
    print("\n📊 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    
    if failed_tests == 0:
        print(f"\n🎉 All tests passed! The multi-agent system is ready to use.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please check the issues above.")
    
    print("\nTest details:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

async def main():
    """Main test function"""
    print("🧪 Multi-Agent System Test Suite")
    print("=" * 60)
    
    # Run tests
    test_results = {}
    
    # Test 1: Environment
    test_results["Environment Setup"] = test_environment()
    
    # Test 2: From-scratch agent (if environment is OK)
    if test_results["Environment Setup"]:
        test_results["From-Scratch Agent"] = test_from_scratch_agent()
    else:
        test_results["From-Scratch Agent"] = False
        print("⏭️  Skipping from-scratch agent test due to environment issues")
    
    # Test 3: Multi-agent system (if previous tests passed)
    if test_results["Environment Setup"]:
        test_results["Multi-Agent System"] = await test_multi_agent_system()
    else:
        test_results["Multi-Agent System"] = False
        print("⏭️  Skipping multi-agent system test due to environment issues")
    
    # Print summary
    print_test_summary(test_results)
    
    # Return overall result
    return all(test_results.values())

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 