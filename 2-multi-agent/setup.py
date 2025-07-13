#!/usr/bin/env python3
"""
Setup script for the Multi-Agent System module
This script helps workshop attendees get started quickly with the multi-agent system.
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_env_file():
    """Help user set up .env file"""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    print("📝 Setting up .env file...")
    print("You need to provide your OpenAI API key.")
    print("Get it from: https://platform.openai.com/api-keys")
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ API key is required")
        return False
    
    # Create .env file
    with open(env_file, "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
        f.write("# Optional: Add Composio API key if you have one\n")
        f.write("# COMPOSIO_API_KEY=your_composio_key_here\n")
    
    print("✅ .env file created successfully!")
    return True

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
        print("✅ Agent imports successful!")
        
        from multi_agent_system import MultiAgentSystem
        print("✅ Multi-agent system import successful!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def test_agent_initialization():
    """Test that agents can be initialized"""
    print("🤖 Testing agent initialization...")
    
    try:
        from agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
        
        # Test agent creation (don't run them, just initialize)
        planner = PlannerAgent()
        coder = CoderAgent() 
        reviewer = ReviewerAgent()
        tester = TesterAgent()
        
        print("✅ All agents initialized successfully!")
        
        # Show agent configurations
        print("\n📊 Agent Configuration:")
        print(f"  Planner: {planner.model} (temp: {planner.temperature})")
        print(f"  Coder: {coder.model} (temp: {coder.temperature})")
        print(f"  Reviewer: {reviewer.model} (temp: {reviewer.temperature})")
        print(f"  Tester: {tester.model} (temp: {tester.temperature})")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Multi-Agent System - Module 2")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return
    
    # Step 3: Set up environment file
    if not setup_env_file():
        return
    
    # Step 4: Test imports
    if not test_imports():
        return
    
    # Step 5: Test agent initialization
    if not test_agent_initialization():
        print("\n⚠️  Setup completed but agent initialization failed.")
        print("Please check your API key and dependencies.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Try: python multi_agent_system.py")
    print("2. Or: python examples.py")
    print("3. Or: python multi_agent_system.py 'Create a sorting algorithm'")
    print("\n🧠 Key Concepts to Explore:")
    print("• Agent specialization and separation of concerns")
    print("• Cost optimization through strategic model selection")
    print("• Handoff mechanisms and workflow coordination")
    print("• Real-world software development team patterns")
    print("\nHappy multi-agent coding! 🤖🤖🤖")

if __name__ == "__main__":
    main() 