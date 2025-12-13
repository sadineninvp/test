#!/usr/bin/env python3
"""
Test script for Command Center - Phase 3 (LLM-powered)
Tests LLM function calling and request understanding
"""

import os
import sys
from command_center import LLMCommandCenter


def test_llm_command_center():
    """Test LLM-powered Command Center"""
    print("=" * 60)
    print("Testing Command Center - Phase 3 (LLM-Powered)")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nTo test Phase 3, set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr pass it as an argument:")
        print("  OPENAI_API_KEY='your-key' python test_llm_command_center.py")
        sys.exit(1)
    
    print(f"✓ API Key found (starting with: {api_key[:10]}...)")
    print()
    
    try:
        center = LLMCommandCenter(api_key=api_key, model="gpt-4o-mini")
    except Exception as e:
        print(f"❌ Error initializing LLM Command Center: {e}")
        sys.exit(1)
    
    # Test 1: Simple command
    print("Test 1: Simple command execution")
    print("-" * 60)
    result = center.handle("run the command 'whoami'")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 2: Natural language request
    print("Test 2: Natural language request")
    print("-" * 60)
    result = center.handle("what's my current username?")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 3: System information
    print("Test 3: System information")
    print("-" * 60)
    result = center.handle("tell me about my system")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 4: Command with explanation
    print("Test 4: Command with explanation")
    print("-" * 60)
    result = center.handle("list the files in the current directory")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print()
    
    # Test 5: Available tools
    print("Test 5: Available tools")
    print("-" * 60)
    tools = center.get_available_tools()
    print(f"Available tools: {', '.join(tools)}")
    print()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nPhase 3 is working! The LLM can understand natural language")
    print("and call the appropriate Action Agent functions.")
    print("\nTo test with API server:")
    print("  uvicorn command_center.api:app --reload")
    print("\nThen test with:")
    print('  curl -X POST http://localhost:8000/api/execute \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"request": "what is my username?", "use_llm": true}\'')


if __name__ == "__main__":
    try:
        test_llm_command_center()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

