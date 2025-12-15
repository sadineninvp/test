#!/usr/bin/env python3
"""
Interactive Test Script - Continuous session for testing IQIDE
Uses Option 1 approach: Single Python process with persistent client
"""

import sys
from client import CommandCenterClient, ResultFormatter

def main():
    """Interactive test session"""
    print("=" * 60)
    print("IQIDE Interactive Test Session")
    print("=" * 60)
    print()
    print("This session maintains state across all requests.")
    print("Commands executed in the same session share the same working directory.")
    print()
    print("Commands:")
    print("  'exit' or 'quit' - Exit the session")
    print("  'help' - Show this help message")
    print("  '--llm' - Use LLM mode (default)")
    print("  '--no-llm' - Use hardcoded routing mode")
    print()
    print("Example:")
    print("  iqide> what is the current directory?")
    print("  iqide> go to /Users")
    print("  iqide> what directory are you in?")
    print()
    print("-" * 60)
    print()
    
    # Create client once - persists for entire session
    try:
        client = CommandCenterClient()
        formatter = ResultFormatter()
        
        # Check server health
        print("Checking server connection...")
        if not client.health_check():
            print("❌ Cannot connect to Command Center server!")
            print("Make sure the server is running:")
            print("  uvicorn command_center.api:app --reload")
            sys.exit(1)
        
        print("✅ Connected to server")
        print()
        
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        sys.exit(1)
    
    # Default to LLM mode
    use_llm = True
    
    print("Starting interactive session...")
    print("(Type 'help' for commands, 'exit' to quit)")
    print()
    
    # Interactive loop
    while True:
        try:
            # Get user input
            prompt = "iqide> " if use_llm else "iqide(hardcoded)> "
            user_input = input(prompt).strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            if user_input.lower() == 'help':
                print()
                print("Commands:")
                print("  'exit' or 'quit' - Exit the session")
                print("  'help' - Show this help")
                print("  '--llm' - Switch to LLM mode (default)")
                print("  '--no-llm' - Switch to hardcoded routing mode")
                print("  Any other input - Send as request to Command Center")
                print()
                continue
            
            # Handle mode switching
            if user_input == '--llm':
                use_llm = True
                print("Switched to LLM mode")
                continue
            
            if user_input == '--no-llm':
                use_llm = False
                print("Switched to hardcoded routing mode")
                continue
            
            # Execute request
            try:
                result = client.execute(user_input, use_llm=use_llm)
                
                # Format and display result
                formatted = formatter.format(result)
                print(formatted)
                
            except KeyboardInterrupt:
                print("\nRequest cancelled")
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            # Handle Ctrl+D
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()


