#!/usr/bin/env python3
"""
IQIDE CLI Client - Phase 4
Command-line interface for Command Center
"""

import sys
import argparse
from typing import Optional

from .api_client import CommandCenterClient
from .config import Config
from .formatter import ResultFormatter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="IQIDE - Intelligent Query IDE Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "what is my username?"
  %(prog)s "run ls -la" --no-llm
  %(prog)s "restart nginx" --llm
  %(prog)s --config-set api_url http://example.com:8000
  %(prog)s --health-check

Environment Variables:
  IQIDE_API_URL      - Command Center API URL
  IQIDE_USE_LLM      - Default to use LLM (true/false)
        """
    )
    
    parser.add_argument(
        "request",
        nargs="?",
        help="Request to send to Command Center"
    )
    
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM-powered mode (Phase 3)"
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Use hardcoded routing mode (Phase 2)"
    )
    
    parser.add_argument(
        "--api-url",
        help="Command Center API URL (overrides config)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        help="Request timeout in seconds"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Check if Command Center server is reachable"
    )
    
    parser.add_argument(
        "--config-get",
        metavar="KEY",
        help="Get config value"
    )
    
    parser.add_argument(
        "--config-set",
        metavar=("KEY", "VALUE"),
        nargs=2,
        help="Set config value"
    )
    
    parser.add_argument(
        "--list-actions",
        action="store_true",
        help="List supported actions (Phase 2)"
    )
    
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools (Phase 3)"
    )
    
    args = parser.parse_args()
    
    # Initialize config
    config = Config()
    
    # Handle config commands
    if args.config_get:
        value = config.get(args.config_get)
        print(value)
        return 0
    
    if args.config_set:
        key, value = args.config_set
        # Try to convert value types
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        elif value.isdigit():
            value = int(value)
        config.set(key, value)
        print(f"Config '{key}' set to: {value}")
        return 0
    
    # Initialize client
    api_url = args.api_url or config.get_api_url()
    timeout = args.timeout or config.get_timeout()
    client = CommandCenterClient(api_url=api_url, timeout=timeout, config=config)
    
    # Health check
    if args.health_check:
        is_healthy = client.health_check()
        if is_healthy:
            print(f"✅ Command Center server is reachable at {api_url}")
            return 0
        else:
            print(f"❌ Command Center server is not reachable at {api_url}")
            print("\nMake sure the server is running:")
            print("  uvicorn command_center.api:app --reload")
            return 1
    
    # List actions (Phase 2)
    if args.list_actions:
        result = client.get_supported_actions()
        if "error" in result:
            print(f"Error: {result['error']}")
            return 1
        actions = result.get("supported_actions", [])
        print("Supported actions (Phase 2 - Hardcoded):")
        for action in actions:
            print(f"  - {action}")
        return 0
    
    # List tools (Phase 3)
    if args.list_tools:
        result = client.get_tools()
        if "error" in result:
            print(f"Error: {result['error']}")
            return 1
        tools = result.get("available_tools", [])
        print("Available tools (Phase 3 - LLM):")
        for tool in tools:
            print(f"  - {tool}")
        return 0
    
    # Execute request
    if not args.request:
        parser.print_help()
        return 1
    
    # Determine use_llm
    use_llm = None
    if args.llm:
        use_llm = True
    elif args.no_llm:
        use_llm = False
    # Otherwise use config default
    
    # Execute
    result = client.execute(args.request, use_llm=use_llm)
    
    # Format output
    output_format = "json" if args.json else config.get_output_format()
    formatted = ResultFormatter.format(result, output_format=output_format)
    
    print(formatted)
    
    # Return exit code based on success
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    sys.exit(main())

