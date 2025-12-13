#!/usr/bin/env python3
"""
Test script for Action Agent - Phase 1
Run this to test the command executor
"""

from action_agent import CommandExecutor, ActionLogger


def test_basic_commands():
    """Test basic command execution"""
    print("=" * 60)
    print("Testing Action Agent - Phase 1")
    print("=" * 60)
    print()
    
    # Create executor
    executor = CommandExecutor()
    
    # Test 1: Simple echo command
    print("Test 1: Simple echo command")
    print("-" * 60)
    result = executor.run("echo 'Hello, Action Agent!'")
    print(f"Success: {result['success']}")
    print(f"Output: {result['output']}")
    print(f"Execution time: {result['execution_time']:.3f}s")
    print()
    
    # Test 2: List current directory
    print("Test 2: List current directory")
    print("-" * 60)
    result = executor.run("ls -la")
    print(f"Success: {result['success']}")
    print(f"Output (first 200 chars):\n{result['output'][:200]}...")
    print()
    
    # Test 3: Get system info
    print("Test 3: System information")
    print("-" * 60)
    sys_info = executor.get_system_info()
    for key, value in sys_info.items():
        print(f"{key}: {value}")
    print()
    
    # Test 4: Whoami command
    print("Test 4: Who am I?")
    print("-" * 60)
    result = executor.run("whoami")
    print(f"Output: {result['output'].strip()}")
    print()
    
    # Test 5: Check recent logs
    print("Test 5: Recent action logs")
    print("-" * 60)
    logger = ActionLogger()
    recent_logs = logger.get_recent_logs(limit=5)
    print(f"Found {len(recent_logs)} recent log entries:")
    for log in recent_logs:
        status = "✓" if log["success"] else "✗"
        print(f"  {status} [{log['timestamp']}] {log['action_type']}: {log['action'][:50]}")
    print()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nCheck logs/action_agent.log for detailed audit logs")


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    print()
    
    executor = CommandExecutor()
    
    # Test invalid command
    print("Test: Invalid command")
    print("-" * 60)
    result = executor.run("this_command_does_not_exist_12345")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    print(f"Return code: {result['return_code']}")
    print()


if __name__ == "__main__":
    try:
        test_basic_commands()
        test_error_handling()
    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()

