#!/usr/bin/env python3
"""
Setup script for the Toy Example module
This script helps workshop attendees get started quickly.
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

def run_test():
    """Run a quick test to verify everything works"""
    print("🧪 Running quick test...")
    
    try:
        # Import and test the REPL function
        from coding_agent import run_python_code
        
        result = run_python_code("print('Setup test successful!')")
        if "Setup test successful!" in result:
            print("✅ Quick test passed!")
            return True
        else:
            print(f"❌ Quick test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Toy Example - Coding Agent")
    print("=" * 50)
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return
    
    # Step 3: Set up environment file
    if not setup_env_file():
        return
    
    # Step 4: Run a quick test
    if not run_test():
        print("\n⚠️  Setup completed but tests failed.")
        print("Please check your API key and try running 'python test_agent.py'")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Try: python coding_agent.py")
    print("2. Or: python examples.py")
    print("3. Or: python test_agent.py")
    print("\nHappy coding! 🤖")

if __name__ == "__main__":
    main() 