#!/usr/bin/env python3
"""
Test script for IQIDE Client - Phase 4
Tests CLI client functionality
"""

import sys
from client import CommandCenterClient, Config, ResultFormatter


def test_client():
    """Test client components"""
    print("=" * 60)
    print("Testing IQIDE Client - Phase 4")
    print("=" * 60)
    print()
    
    # Test 1: Configuration
    print("Test 1: Configuration")
    print("-" * 60)
    config = Config()
    print(f"API URL: {config.get_api_url()}")
    print(f"Default use_llm: {config.get_default_use_llm()}")
    print(f"Timeout: {config.get_timeout()}")
    print()
    
    # Test 2: API Client initialization
    print("Test 2: API Client")
    print("-" * 60)
    client = CommandCenterClient(config=config)
    print(f"Client initialized with API URL: {client.api_url}")
    print()
    
    # Test 3: Health check
    print("Test 3: Health Check")
    print("-" * 60)
    is_healthy = client.health_check()
    if is_healthy:
        print("✅ Command Center server is reachable")
    else:
        print("❌ Command Center server is not reachable")
        print("   (This is OK if server is not running)")
    print()
    
    # Test 4: Test request (only if server is running)
    if is_healthy:
        print("Test 4: Execute Request (Phase 2)")
        print("-" * 60)
        result = client.execute("run whoami", use_llm=False)
        formatted = ResultFormatter.format(result)
        print(formatted)
        print()
        
        print("Test 5: Execute Request (Phase 3 - if API key set)")
        print("-" * 60)
        import os
        if os.getenv("OPENAI_API_KEY"):
            result = client.execute("what is my username?", use_llm=True)
            formatted = ResultFormatter.format(result)
            print(formatted)
        else:
            print("⚠️  OPENAI_API_KEY not set, skipping Phase 3 test")
        print()
    
    print("=" * 60)
    print("Client tests completed!")
    print("=" * 60)
    print("\nTo use the CLI:")
    print("  python3 iqide.py 'your request here'")
    print("\nOr make it executable and run directly:")
    print("  ./iqide.py 'your request here'")


if __name__ == "__main__":
    try:
        test_client()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

