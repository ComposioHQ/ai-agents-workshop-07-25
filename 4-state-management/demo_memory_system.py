#!/usr/bin/env python3
"""
Memory System Demonstration

This script demonstrates the key features of the state management system:
1. Project memory creation and persistence
2. Conversation history tracking
3. Automatic summarization
4. Memory-aware agent interactions
"""

import asyncio
import os
import json
from datetime import datetime
from state_management_multi_agent_system import (
    MemoryManager, 
    ProjectMemory, 
    ConversationEntry,
    run_multi_agent_system_with_memory
)

def demo_memory_manager():
    """Demonstrate the MemoryManager functionality"""
    print("🧠 Memory Manager Demo")
    print("=" * 50)
    
    # Create a memory manager for a demo project
    memory_manager = MemoryManager("DemoProject")
    
    # Add some conversation entries
    print("📝 Adding conversation entries...")
    memory_manager.add_conversation_entry(
        agent_name="Planner",
        message_type="input",
        content="Plan a web API with authentication",
        tokens_used=150
    )
    
    memory_manager.add_conversation_entry(
        agent_name="Planner",
        message_type="output",
        content="I'll create a plan for a REST API with JWT authentication...",
        tokens_used=300
    )
    
    memory_manager.add_conversation_entry(
        agent_name="Planner",
        message_type="handoff",
        content="Handing off to Coder for implementation",
        tokens_used=50
    )
    
    # Update project memory
    print("📚 Updating project memory...")
    memory_manager.update_project_info(
        architecture_decisions="Using Flask framework with JWT for authentication",
        files_created="app.py",
        successful_patterns="REST API design pattern",
        next_steps="Implement user registration endpoint"
    )
    
    # Display memory context
    print("\n🔍 Current Memory Context:")
    print(memory_manager.get_context_summary())
    
    # Save memory
    memory_manager.save_project_memory()
    print("\n💾 Memory saved to file")
    
    return memory_manager

def demo_conversation_summarization():
    """Demonstrate automatic conversation summarization"""
    print("\n📝 Conversation Summarization Demo")
    print("=" * 50)
    
    # Create memory manager with low threshold for demo
    memory_manager = MemoryManager("SummarizationDemo")
    memory_manager.max_conversation_length = 5  # Low threshold for demo
    
    # Add multiple conversation entries to trigger summarization
    agents = ["Planner", "Coder", "Reviewer", "Triage"]
    message_types = ["input", "output", "handoff"]
    
    print("📝 Adding multiple conversation entries...")
    for i in range(10):
        memory_manager.add_conversation_entry(
            agent_name=agents[i % len(agents)],
            message_type=message_types[i % len(message_types)],
            content=f"Message {i+1}: This is a sample conversation entry",
            tokens_used=50 + i * 10
        )
    
    print(f"📊 Conversation history length: {len(memory_manager.conversation_history)}")
    
    # The summarization should have been triggered automatically
    if len(memory_manager.conversation_history) <= 5:
        print("✅ Automatic summarization occurred!")
        for entry in memory_manager.conversation_history:
            if entry.message_type == "summary":
                print(f"📄 Summary: {entry.content}")
                break
    
    return memory_manager

def demo_project_memory_persistence():
    """Demonstrate project memory persistence"""
    print("\n💾 Project Memory Persistence Demo")
    print("=" * 50)
    
    project_name = "PersistenceDemo"
    
    # Create first memory manager and add some data
    print("📝 Creating initial project memory...")
    memory_manager1 = MemoryManager(project_name)
    memory_manager1.update_project_info(
        original_requirements="Build a task management system",
        architecture_decisions="Using SQLite database",
        files_created="models.py",
        successful_patterns="MVC pattern"
    )
    memory_manager1.save_project_memory()
    
    # Create second memory manager for same project (should load existing)
    print("📂 Loading existing project memory...")
    memory_manager2 = MemoryManager(project_name)
    
    # Verify data was loaded
    if memory_manager2.project_memory.original_requirements == "Build a task management system":
        print("✅ Project memory loaded successfully!")
        print(f"📊 Files created: {memory_manager2.project_memory.files_created}")
        print(f"🏗️  Architecture decisions: {memory_manager2.project_memory.architecture_decisions}")
    
    # Add more data to demonstrate persistence
    memory_manager2.update_project_info(
        files_created="controllers.py",
        lessons_learned="SQLite is perfect for small applications"
    )
    
    print(f"📈 Updated files: {memory_manager2.project_memory.files_created}")
    
    return memory_manager2

def demo_file_tracking():
    """Demonstrate file creation and modification tracking"""
    print("\n📁 File Tracking Demo")
    print("=" * 50)
    
    # Create memory manager
    memory_manager = MemoryManager("FileTrackingDemo")
    
    # Simulate file creation events (as would happen in hooks)
    print("📝 Simulating file creation events...")
    
    # File 1: Create main.py
    memory_manager.add_conversation_entry(
        agent_name="Coder",
        message_type="file_created",
        content="Created file: main.py",
        metadata={"file_path": "main.py", "tool_name": "filetool_create_file"}
    )
    memory_manager.update_project_info(files_created="main.py")
    
    # File 2: Create utils.py
    memory_manager.add_conversation_entry(
        agent_name="Coder",
        message_type="file_created",
        content="Created file: utils.py",
        metadata={"file_path": "utils.py", "tool_name": "filetool_create_file"}
    )
    memory_manager.update_project_info(files_created="utils.py")
    
    # File 3: Modify main.py
    memory_manager.add_conversation_entry(
        agent_name="Coder",
        message_type="file_modified",
        content="Modified file: main.py",
        metadata={"file_path": "main.py", "tool_name": "filetool_edit_file"}
    )
    memory_manager.update_project_info(files_modified="main.py")
    
    # File 4: Create tests.py
    memory_manager.add_conversation_entry(
        agent_name="Coder",
        message_type="file_created",
        content="Created file: tests.py",
        metadata={"file_path": "tests.py", "tool_name": "filetool_create_file"}
    )
    memory_manager.update_project_info(files_created="tests.py")
    
    # Show results
    print(f"✅ Files created: {memory_manager.project_memory.files_created}")
    print(f"✏️ Files modified: {memory_manager.project_memory.files_modified}")
    
    # Show conversation history with file events
    file_events = [e for e in memory_manager.conversation_history if e.message_type in ["file_created", "file_modified"]]
    print(f"📝 File events recorded: {len(file_events)}")
    
    for event in file_events:
        print(f"  • {event.timestamp.strftime('%H:%M:%S')} - {event.agent_name}: {event.content}")
    
    return memory_manager

async def demo_full_workflow():
    """Demonstrate the full workflow with memory"""
    print("\n🚀 Full Workflow Demo")
    print("=" * 50)
    
    # First request
    print("📝 First Request: Initial system creation...")
    request1 = """
    Create a simple Python calculator that:
    1. Supports basic arithmetic operations
    2. Has error handling for division by zero
    3. Includes unit tests
    """
    
    result1 = await run_multi_agent_system_with_memory(
        user_request=request1,
        project_name="CalculatorProject"
    )
    print(f"✅ First request completed")
    
    # Second request - should build on memory
    print("\n📝 Second Request: Enhancement based on memory...")
    request2 = """
    Enhance the calculator with:
    1. Scientific functions (sin, cos, log)
    2. Memory functions (store, recall, clear)
    3. History tracking
    """
    
    result2 = await run_multi_agent_system_with_memory(
        user_request=request2,
        project_name="CalculatorProject"
    )
    print(f"✅ Second request completed")
    
    # Show memory file
    memory_file = "memory/CalculatorProject_memory.json"
    if os.path.exists(memory_file):
        print(f"\n📄 Memory file created: {memory_file}")
        with open(memory_file, 'r') as f:
            memory_data = json.load(f)
            print(f"📊 Files created: {len(memory_data.get('files_created', []))}")
            print(f"🏗️  Architecture decisions: {len(memory_data.get('architecture_decisions', []))}")
            print(f"📚 Lessons learned: {len(memory_data.get('lessons_learned', []))}")

def main():
    """Main demonstration function"""
    print("🤖 State Management System Demo")
    print("=" * 60)
    
    # Demo 1: Basic memory manager functionality
    demo_memory_manager()
    
    # Demo 2: Conversation summarization
    demo_conversation_summarization()
    
    # Demo 3: Project memory persistence
    demo_project_memory_persistence()
    
    # Demo 4: File tracking
    demo_file_tracking()
    
    # Demo 5: Full workflow (if OpenAI API key is available)
    if os.getenv("OPENAI_API_KEY"):
        print("\n🔑 OpenAI API Key found - running full workflow demo...")
        asyncio.run(demo_full_workflow())
    else:
        print("\n⚠️  OpenAI API Key not found - skipping full workflow demo")
        print("Set OPENAI_API_KEY environment variable to run the full demo")
    
    print("\n✅ All demos completed!")
    print("🧠 Check the 'memory/' directory for generated memory files")

if __name__ == "__main__":
    main() 