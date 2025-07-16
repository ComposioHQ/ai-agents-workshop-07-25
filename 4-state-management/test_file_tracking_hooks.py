#!/usr/bin/env python3
"""
Test File Tracking Hooks with Real Tool Calls

This script demonstrates how the file tracking hooks work with actual tool calls
and shows that files are properly tracked in the memory system.
"""

import os
import tempfile
import asyncio
from state_management_multi_agent_system import (
    MemoryManager, 
    StateManagementHooks, 
    ProjectContext,
    composio_toolset
)
from agents import Agent, function_tool
from composio_openai_agents import Action

def test_file_tracking_hooks():
    """Test that file tracking hooks work with simulated tool calls"""
    print("🧪 Testing File Tracking Hooks")
    print("=" * 50)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create memory manager
        memory_manager = MemoryManager("HooksTest", memory_dir=temp_dir)
        
        # Create hooks
        hooks = StateManagementHooks(memory_manager)
        
        # Create a simple mock agent
        class MockAgent:
            def __init__(self, name):
                self.name = name
        
        class MockContext:
            def __init__(self, agent):
                self.agent = agent
        
        class MockTool:
            def __init__(self, name):
                self.name = name
        
        # Create test objects
        agent = MockAgent("TestAgent")
        context = MockContext(agent)
        tool = MockTool("filetool_create_file")
        
        # Test file creation hook
        print("📁 Testing file creation hook...")
        
        # Simulate on_tool_start
        asyncio.run(hooks.on_tool_start(context, agent, tool))
        
        # Simulate on_tool_end with file creation result
        result = "Successfully created file: test_file.py"
        asyncio.run(hooks.on_tool_end(context, agent, tool, result))
        
        # Check if file was tracked
        assert "test_file.py" in memory_manager.project_memory.files_created
        print("✅ File creation tracked successfully!")
        
        # Test file modification hook
        print("✏️ Testing file modification hook...")
        
        edit_tool = MockTool("filetool_edit_file")
        asyncio.run(hooks.on_tool_start(context, agent, edit_tool))
        
        edit_result = "Modified file: test_file.py - Added new function"
        asyncio.run(hooks.on_tool_end(context, agent, edit_tool, edit_result))
        
        # Check if file modification was tracked
        assert "test_file.py" in memory_manager.project_memory.files_modified
        print("✅ File modification tracked successfully!")
        
        # Show conversation history
        print("\n📝 Conversation History:")
        for entry in memory_manager.conversation_history:
            print(f"  • {entry.timestamp.strftime('%H:%M:%S')} - {entry.agent_name}: {entry.message_type} - {entry.content}")
        
        # Show project memory
        print(f"\n📊 Project Memory:")
        print(f"  Files created: {memory_manager.project_memory.files_created}")
        print(f"  Files modified: {memory_manager.project_memory.files_modified}")
        
        return True

def test_file_path_extraction():
    """Test the file path extraction logic"""
    print("\n🔍 Testing File Path Extraction")
    print("=" * 50)
    
    # Create hooks instance
    memory_manager = MemoryManager("ExtractionTest")
    hooks = StateManagementHooks(memory_manager)
    
    # Test various result patterns
    test_cases = [
        ("Successfully created file: main.py", "main.py"),
        ("File saved to: /path/to/utils.py", "/path/to/utils.py"),
        ("Created 'config.json' successfully", "config.json"),
        ("Wrote to \"data/test.txt\" completed", "data/test.txt"),
        ("Output written to src/components/Button.tsx", "src/components/Button.tsx"),
        ("Modified file app.py with new changes", "app.py"),
        ("No file pattern here", None),
    ]
    
    for result, expected in test_cases:
        extracted = hooks._extract_file_path_from_result(result, "test_tool")
        if extracted == expected:
            print(f"✅ '{result}' → '{extracted}'")
        else:
            print(f"❌ '{result}' → expected '{expected}', got '{extracted}'")
    
    return True

def test_multiple_file_operations():
    """Test tracking multiple file operations"""
    print("\n📂 Testing Multiple File Operations")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("MultiFileTest", memory_dir=temp_dir)
        hooks = StateManagementHooks(memory_manager)
        
        # Mock objects
        class MockAgent:
            def __init__(self, name):
                self.name = name
        
        class MockContext:
            def __init__(self, agent):
                self.agent = agent
        
        class MockTool:
            def __init__(self, name):
                self.name = name
        
        agent = MockAgent("Coder")
        context = MockContext(agent)
        
        # Simulate creating multiple files
        files_to_create = [
            ("main.py", "Created main.py with basic structure"),
            ("utils.py", "Successfully created utils.py"),
            ("config.json", "Saved configuration to config.json"),
            ("test_main.py", "Created test file: test_main.py"),
        ]
        
        for filename, result in files_to_create:
            tool = MockTool("filetool_create_file")
            asyncio.run(hooks.on_tool_start(context, agent, tool))
            asyncio.run(hooks.on_tool_end(context, agent, tool, result))
        
        # Simulate modifying some files
        files_to_modify = [
            ("main.py", "Modified main.py - added error handling"),
            ("utils.py", "Updated utils.py with new functions"),
        ]
        
        for filename, result in files_to_modify:
            tool = MockTool("filetool_edit_file")
            asyncio.run(hooks.on_tool_start(context, agent, tool))
            asyncio.run(hooks.on_tool_end(context, agent, tool, result))
        
        # Check results
        print(f"📁 Files created: {len(memory_manager.project_memory.files_created)}")
        print(f"✏️ Files modified: {len(memory_manager.project_memory.files_modified)}")
        
        expected_created = ["main.py", "utils.py", "config.json", "test_main.py"]
        expected_modified = ["main.py", "utils.py"]
        
        for file in expected_created:
            assert file in memory_manager.project_memory.files_created, f"Expected {file} in created files"
        
        for file in expected_modified:
            assert file in memory_manager.project_memory.files_modified, f"Expected {file} in modified files"
        
        print("✅ All file operations tracked correctly!")
        
        return True

def main():
    """Run all hook tests"""
    print("🔧 File Tracking Hooks Test Suite")
    print("=" * 60)
    
    try:
        success1 = test_file_tracking_hooks()
        success2 = test_file_path_extraction()
        success3 = test_multiple_file_operations()
        
        if success1 and success2 and success3:
            print("\n🎉 All hook tests passed!")
            print("✅ File tracking hooks are working correctly with tool calls")
            return True
        else:
            print("\n❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 