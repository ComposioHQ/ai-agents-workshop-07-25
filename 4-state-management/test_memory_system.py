#!/usr/bin/env python3
"""
Test Suite for State Management System

This script tests the key functionality of the memory system to ensure it works correctly.
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
from state_management_multi_agent_system import (
    MemoryManager, 
    ProjectMemory, 
    ConversationEntry,
    ProjectContext
)

def test_memory_manager_creation():
    """Test MemoryManager creation and initialization"""
    print("🧪 Test: MemoryManager creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        
        # Check that project memory was created
        assert memory_manager.project_memory is not None
        assert memory_manager.project_memory.project_name == "TestProject"
        assert memory_manager.conversation_history == []
        
        print("✅ MemoryManager creation test passed")
        return True

def test_conversation_entry_tracking():
    """Test conversation entry tracking"""
    print("🧪 Test: Conversation entry tracking...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        
        # Add conversation entries
        memory_manager.add_conversation_entry(
            agent_name="TestAgent",
            message_type="input",
            content="Test message",
            tokens_used=100
        )
        
        # Check that entry was added
        assert len(memory_manager.conversation_history) == 1
        entry = memory_manager.conversation_history[0]
        assert entry.agent_name == "TestAgent"
        assert entry.message_type == "input"
        assert entry.content == "Test message"
        assert entry.tokens_used == 100
        
        print("✅ Conversation entry tracking test passed")
        return True

def test_project_memory_persistence():
    """Test project memory persistence"""
    print("🧪 Test: Project memory persistence...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create first memory manager
        memory_manager1 = MemoryManager("TestProject", memory_dir=temp_dir)
        memory_manager1.update_project_info(
            original_requirements="Test requirements",
            architecture_decisions="Test decision",
            files_created="test.py"
        )
        memory_manager1.save_project_memory()
        
        # Create second memory manager (should load existing)
        memory_manager2 = MemoryManager("TestProject", memory_dir=temp_dir)
        
        # Verify data persistence
        assert memory_manager2.project_memory.original_requirements == "Test requirements"
        assert "Test decision" in memory_manager2.project_memory.architecture_decisions
        assert "test.py" in memory_manager2.project_memory.files_created
        
        print("✅ Project memory persistence test passed")
        return True

def test_conversation_summarization():
    """Test automatic conversation summarization"""
    print("🧪 Test: Conversation summarization...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        memory_manager.max_conversation_length = 3  # Low threshold for testing
        
        # Add enough entries to trigger summarization (need > max_conversation_length)
        for i in range(7):  # 7 > 3, so should trigger
            memory_manager.add_conversation_entry(
                agent_name=f"Agent{i}",
                message_type="input",
                content=f"Message {i}",
                tokens_used=50
            )
        
        # Check that summarization occurred
        print(f"History length after adding 7 entries: {len(memory_manager.conversation_history)}")
        print(f"Entry types: {[entry.message_type for entry in memory_manager.conversation_history]}")
        assert len(memory_manager.conversation_history) <= 4  # 1 summary + 3 recent (after summarization)
        
        # Check that a summary entry exists
        has_summary = any(entry.message_type == "summary" for entry in memory_manager.conversation_history)
        assert has_summary
        
        print("✅ Conversation summarization test passed")
        return True

def test_context_summary():
    """Test context summary generation"""
    print("🧪 Test: Context summary generation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        memory_manager.update_project_info(
            original_requirements="Build a test system",
            files_created="main.py",
            current_blockers="Need API key"
        )
        
        # Generate context summary
        context_summary = memory_manager.get_context_summary()
        
        # Check that summary contains expected information
        assert "TestProject" in context_summary
        assert "Build a test system" in context_summary
        assert "main.py" in context_summary
        assert "Need API key" in context_summary
        
        print("✅ Context summary generation test passed")
        return True

def test_project_context_integration():
    """Test ProjectContext integration with memory"""
    print("🧪 Test: ProjectContext integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create project context
        context = ProjectContext(
            project_name="TestProject",
            requirements="Test requirements",
            current_stage="testing"
        )
        
        # Override memory manager with temp directory
        context.memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        
        # Check that memory manager was integrated
        assert context.memory_manager is not None
        assert context.memory_manager.project_memory.project_name == "TestProject"
        
        print("✅ ProjectContext integration test passed")
        return True

def test_memory_updates():
    """Test memory update functionality"""
    print("🧪 Test: Memory update functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        
        # Test single updates
        memory_manager.update_project_info(
            original_requirements="Initial requirements"
        )
        assert memory_manager.project_memory.original_requirements == "Initial requirements"
        
        # Test list updates
        memory_manager.update_project_info(
            files_created="file1.py"
        )
        memory_manager.update_project_info(
            files_created="file2.py"
        )
        
        assert len(memory_manager.project_memory.files_created) == 2
        assert "file1.py" in memory_manager.project_memory.files_created
        assert "file2.py" in memory_manager.project_memory.files_created
        
        print("✅ Memory update functionality test passed")
        return True

def test_json_serialization():
    """Test JSON serialization of project memory"""
    print("🧪 Test: JSON serialization...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        memory_manager.update_project_info(
            original_requirements="Test requirements",
            architecture_decisions="Test decision",
            files_created="test.py"
        )
        
        # Convert to dict and back
        memory_dict = memory_manager.project_memory.to_dict()
        recreated_memory = ProjectMemory.from_dict(memory_dict)
        
        # Check that data is preserved
        assert recreated_memory.project_name == "TestProject"
        assert recreated_memory.original_requirements == "Test requirements"
        assert "Test decision" in recreated_memory.architecture_decisions
        assert "test.py" in recreated_memory.files_created
        
        print("✅ JSON serialization test passed")
        return True

def test_file_tracking():
    """Test file creation and modification tracking"""
    print("🧪 Test: File tracking...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager("TestProject", memory_dir=temp_dir)
        
        # Simulate file creation tracking
        memory_manager.add_conversation_entry(
            agent_name="Coder",
            message_type="file_created",
            content="Created file: main.py",
            metadata={"file_path": "main.py", "tool_name": "filetool_create_file"}
        )
        
        # Update project info as hooks would
        memory_manager.update_project_info(files_created="main.py")
        
        # Simulate file modification
        memory_manager.add_conversation_entry(
            agent_name="Coder",
            message_type="file_modified",
            content="Modified file: main.py",
            metadata={"file_path": "main.py", "tool_name": "filetool_edit_file"}
        )
        
        memory_manager.update_project_info(files_modified="main.py")
        
        # Check that files are tracked
        assert "main.py" in memory_manager.project_memory.files_created
        assert "main.py" in memory_manager.project_memory.files_modified
        
        # Check conversation entries
        file_created_entries = [e for e in memory_manager.conversation_history if e.message_type == "file_created"]
        file_modified_entries = [e for e in memory_manager.conversation_history if e.message_type == "file_modified"]
        
        assert len(file_created_entries) == 1
        assert len(file_modified_entries) == 1
        assert file_created_entries[0].metadata["file_path"] == "main.py"
        assert file_modified_entries[0].metadata["file_path"] == "main.py"
        
        print("✅ File tracking test passed")
        return True

def run_all_tests():
    """Run all tests"""
    print("🧪 Running Memory System Tests")
    print("=" * 50)
    
    tests = [
        test_memory_manager_creation,
        test_conversation_entry_tracking,
        test_project_memory_persistence,
        test_conversation_summarization,
        test_context_summary,
        test_project_context_integration,
        test_memory_updates,
        test_json_serialization,
        test_file_tracking
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed}/{passed + failed} ({(passed/(passed + failed)*100):.1f}%)")
    
    if failed == 0:
        print("\n🎉 All tests passed! Memory system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 