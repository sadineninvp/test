#!/usr/bin/env python3
"""
Test script for Command Center - Phase 2
Tests hardcoded routing and orchestration
"""

from command_center import CommandCenter


def test_command_center():
    """Test Command Center with various requests"""
    print("=" * 60)
    print("Testing Command Center - Phase 2")
    print("=" * 60)
    print()
    
    center = CommandCenter()
    
    # Test 1: Check service
    print("Test 1: Check service status")
    print("-" * 60)
    result = center.handle("check nginx")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 2: Run command
    print("Test 2: Run a command")
    print("-" * 60)
    result = center.handle("run command echo 'Hello from Command Center'")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 3: Simple command
    print("Test 3: Simple command (shorthand)")
    print("-" * 60)
    result = center.handle("run whoami")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 4: List directory
    print("Test 4: List directory")
    print("-" * 60)
    result = center.handle("run ls -la")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message'][:200]}...")  # Truncate long output
    print()
    
    # Test 5: Unknown action
    print("Test 5: Unknown action")
    print("-" * 60)
    result = center.handle("do something weird and crazy")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 6: Supported actions
    print("Test 6: Supported actions")
    print("-" * 60)
    actions = center.get_supported_actions()
    print(f"Supported actions: {', '.join(actions)}")
    print()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nTo test with API server, run:")
    print("  uvicorn command_center.api:app --reload")
    print("\nThen test with:")
    print('  curl -X POST http://localhost:8000/api/execute \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"request": "run whoami"}\'')


if __name__ == "__main__":
    try:
        test_command_center()
    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()

