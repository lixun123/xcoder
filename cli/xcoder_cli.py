#!/usr/bin/env python3
"""
XCoder CLI - Interactive Terminal Interface for XCoder Agent

This module provides a command-line interface for interacting with the XCoder agent,
supporting both chat mode and debug mode with seamless switching between modes.
"""

import sys
import os
import argparse
from typing import Optional, Dict, Any
import json
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Try importing colorama, if not available, use simple colors
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Simple color fallbacks
    class Fore:
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        CYAN = '\033[36m'
        MAGENTA = '\033[35m'
        WHITE = '\033[37m'

    class Style:
        RESET_ALL = '\033[0m'

    def init(**kwargs):
        pass

from core.agents.entry_agent import EntryAgent
from core.agents.code_fix_agent import CodeFixAgent

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class XCoderCLI:
    """Interactive CLI for XCoder Agent."""

    def __init__(self):
        """Initialize the CLI interface."""
        self.current_mode = "chat"  # Default mode: "chat" or "debug"
        self.entry_agent = None
        self.code_fix_agent = None
        self.session_id = None
        self.history = []
        self.config = self._load_config()
        self.chat_memory = {}  # Session-level memory for conversations

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        config_path = os.path.expanduser("~/.xcoder/config.json")
        default_config = {
            "auto_save_history": True,
            "history_file": os.path.expanduser("~/.xcoder/history.json"),
            "theme": {
                "prompt_color": Fore.GREEN,
                "system_color": Fore.CYAN,
                "error_color": Fore.RED,
                "success_color": Fore.GREEN,
                "warning_color": Fore.YELLOW
            }
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self._print_colored(f"Warning: Could not load config: {e}", "warning")

        return default_config

    def _save_config(self):
        """Save configuration to file."""
        config_dir = os.path.expanduser("~/.xcoder")
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, "config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._print_colored(f"Warning: Could not save config: {e}", "warning")

    def _print_colored(self, text: str, color_type: str = "system"):
        """Print colored text based on type."""
        theme = self.config.get("theme", {})
        color_map = {
            "prompt": theme.get("prompt_color", Fore.GREEN),
            "system": theme.get("system_color", Fore.CYAN),
            "error": theme.get("error_color", Fore.RED),
            "success": theme.get("success_color", Fore.GREEN),
            "warning": theme.get("warning_color", Fore.YELLOW)
        }

        color = color_map.get(color_type, Fore.WHITE)
        print(f"{color}{text}{Style.RESET_ALL}")

    def _sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to handle problematic Unicode sequences.

        Args:
            user_input: Raw input string that may contain invalid Unicode

        Returns:
            Cleaned input string safe for JSON serialization
        """
        try:
            # Method 1: Encode to UTF-8 and decode, replacing errors
            cleaned = user_input.encode('utf-8', 'replace').decode('utf-8', 'replace')

            # Method 2: Remove any remaining surrogate characters
            # Surrogates are in the range U+D800 to U+DFFF
            cleaned = ''.join(char for char in cleaned if not (0xD800 <= ord(char) <= 0xDFFF))

            return cleaned
        except UnicodeError:
            # Fallback: Try to recover as much text as possible
            try:
                # Use 'ignore' error handling as last resort
                return user_input.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            except:
                # Ultimate fallback: return safe placeholder
                return "[Input contained invalid characters]"

    def _initialize_agents(self):
        try:
            # self._print_colored("Initializing XCoder agents...", "system")

            # Initialize Entry Agent for chat mode
            if not self.entry_agent:
                # self._print_colored("Loading chat agent...", "system")
                self.entry_agent = EntryAgent()

            # Initialize Code Fix Agent for debug mode
            if not self.code_fix_agent:
                # self._print_colored("Loading debug agent...", "system")
                self.code_fix_agent = CodeFixAgent()

            self._print_colored("Agents initialized successfully!", "success")
            return True

        except Exception as e:
            self._print_colored(f"Failed to initialize agents: {e}", "error")
            return False

    def _print_banner(self):
        """Print the XCoder banner."""
        banner = f"""
{Fore.CYAN}
██╗  ██╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗
╚██╗██╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
 ╚███╔╝ ██║     ██║   ██║██║  ██║█████╗  ██████╔╝
 ██╔██╗ ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
██╔╝ ██╗╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝{Style.RESET_ALL}

{Fore.MAGENTA}               🚀 Intelligent Coding Assistant 🚀{Style.RESET_ALL}
{Fore.GREEN}                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}

{Fore.GREEN}🎯 Current Mode:{Style.RESET_ALL} {Fore.MAGENTA}{self.current_mode.upper()}{Style.RESET_ALL}  {Fore.GREEN}|{Style.RESET_ALL}  {Fore.CYAN}Ready to code!{Style.RESET_ALL} ⚡
{Fore.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
"""
        print(banner)

    def _print_help(self):
        """Print detailed help information."""
        help_text = f"""
{Fore.CYAN}=== XCoder CLI Help ==={Style.RESET_ALL}

{Fore.GREEN}MODES:{Style.RESET_ALL}
  {Fore.YELLOW}Chat Mode{Style.RESET_ALL}   - General conversation and simple tasks
               - Powered by EntryAgent
               - Supports file operations, web search, etc.

  {Fore.YELLOW}Debug Mode{Style.RESET_ALL}  - Complex code analysis and bug fixing
               - Powered by CodeFixAgent
               - Advanced planning and multi-step execution
               - Specialized sub-agents for different tasks

{Fore.GREEN}COMMANDS:{Style.RESET_ALL}
  {Fore.YELLOW}/chat{Style.RESET_ALL}      - Switch to chat mode for general conversation
  {Fore.YELLOW}/debug{Style.RESET_ALL}     - Switch to debug mode for code fixing
  {Fore.YELLOW}/status{Style.RESET_ALL}    - Show current session status and statistics
  {Fore.YELLOW}/config{Style.RESET_ALL}    - Display current configuration settings
  {Fore.YELLOW}/history{Style.RESET_ALL}   - Show conversation history for this session
  {Fore.YELLOW}/clear{Style.RESET_ALL}     - Clear the terminal screen
  {Fore.YELLOW}/help{Style.RESET_ALL}      - Show this help message
  {Fore.YELLOW}/exit{Style.RESET_ALL}      - Exit XCoder CLI

{Fore.GREEN}USAGE EXAMPLES:{Style.RESET_ALL}
  General conversation:
  > What's the weather like?

  Code help in chat mode:
  > How do I read a file in Python?

  Bug fixing in debug mode:
  > Fix the error in my_script.py

  Complex code analysis:
  > Analyze and refactor the authentication module

{Fore.GREEN}CONFIGURATION:{Style.RESET_ALL}
  Configuration file: ~/.xcoder/config.json
  History file: ~/.xcoder/history.json

  You can modify the model, server URL, and other settings
  by editing the configuration file or using the CLI commands.
"""
        print(help_text)

    def _handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.strip().lower()

        if command == "/exit" or command == "/quit":
            self._print_colored("Goodbye! 👋", "success")
            return False

        elif command == "/chat":
            self.current_mode = "chat"
            self._print_colored("Switched to CHAT mode 💬", "success")
            return True

        elif command == "/debug":
            self.current_mode = "debug"
            self._print_colored("Switched to DEBUG mode 🔧", "success")
            return True

        elif command == "/status":
            self._show_status()
            return True

        elif command == "/config":
            self._show_config()
            return True

        elif command == "/history":
            self._show_history()
            return True

        elif command == "/session":
            self._show_session_info()
            return True

        elif command == "/clear":
            os.system('clear' if os.name == 'posix' else 'cls')
            self._print_banner()
            return True

        elif command == "/help":
            self._print_help()
            return True

        else:
            return True  # Continue processing as regular input

    def _show_status(self):
        """Show current session status."""
        # Get session message count
        message_count = 0
        if self.session_id and self.session_id in self.chat_memory:
            message_count = len(self.chat_memory[self.session_id]["messages"])

        status_info = f"""
{Fore.CYAN}=== Session Status ==={Style.RESET_ALL}
{Fore.GREEN}Current Mode:{Style.RESET_ALL} {self.current_mode.upper()}
{Fore.GREEN}Session ID:{Style.RESET_ALL} {self.session_id or "Not set"}
{Fore.GREEN}Session Messages:{Style.RESET_ALL} {message_count}
{Fore.GREEN}LLM Provider:{Style.RESET_ALL} {self.config.get('llm_provider', 'Unknown')}
{Fore.GREEN}Model:{Style.RESET_ALL} {self.config.get('model_name', 'Unknown')}
{Fore.GREEN}Server:{Style.RESET_ALL} {self.config.get('base_url', 'Unknown')}
{Fore.GREEN}History Items:{Style.RESET_ALL} {len(self.history)}
{Fore.GREEN}Agents Loaded:{Style.RESET_ALL} Chat: {self.entry_agent is not None}, Debug: {self.code_fix_agent is not None}
"""
        print(status_info)

    def _show_config(self):
        """Show current configuration."""
        config_text = f"""
{Fore.CYAN}=== Configuration ==={Style.RESET_ALL}
{Fore.GREEN}LLM Provider:{Style.RESET_ALL} {self.config.get('llm_provider')}
{Fore.GREEN}Model:{Style.RESET_ALL} {self.config.get('model_name')}
{Fore.GREEN}Base URL:{Style.RESET_ALL} {self.config.get('base_url')}
{Fore.GREEN}Auto Save History:{Style.RESET_ALL} {self.config.get('auto_save_history')}
{Fore.GREEN}History File:{Style.RESET_ALL} {self.config.get('history_file')}

{Fore.YELLOW}To modify configuration, edit:{Style.RESET_ALL} ~/.xcoder/config.json
"""
        print(config_text)

    def _show_history(self):
        """Show conversation history."""
        if not self.history:
            self._print_colored("No conversation history in this session.", "warning")
            return

        self._print_colored("=== Session History ===", "system")
        for i, item in enumerate(self.history, 1):
            print(f"{Fore.GREEN}{i}. [{item['timestamp']}]{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}User:{Style.RESET_ALL} {item['user'][:100]}...")
            print(f"   {Fore.CYAN}Bot:{Style.RESET_ALL} {item['bot'][:100]}...")
            print()

    def _show_session_info(self):
        """Show detailed session information."""
        if not self.session_id or self.session_id not in self.chat_memory:
            self._print_colored("No active session found.", "warning")
            return

        session_data = self.chat_memory[self.session_id]
        self._print_colored(f"=== Session Information ===", "system")
        print(f"{Fore.GREEN}Session ID:{Style.RESET_ALL} {self.session_id}")
        print(f"{Fore.GREEN}Created At:{Style.RESET_ALL} {session_data.get('created_at', 'Unknown')}")
        print(f"{Fore.GREEN}Message Count:{Style.RESET_ALL} {len(session_data['messages'])}")
        print(f"{Fore.GREEN}Mode History:{Style.RESET_ALL} {' -> '.join(session_data.get('mode_history', []))}")

        # Show recent messages
        messages = session_data["messages"][-6:]  # Last 6 messages
        if messages:
            print(f"\n{Fore.CYAN}Recent Messages:{Style.RESET_ALL}")
            for i, msg in enumerate(messages):
                role_color = Fore.YELLOW if msg["role"] == "user" else Fore.CYAN
                print(f"  {role_color}{msg['role'].capitalize()}:{Style.RESET_ALL} {msg['content'][:80]}...")

    def _save_to_history(self, user_input: str, bot_response: str):
        """Save conversation to history."""
        # Sanitize both input and response before saving to prevent encoding issues
        clean_user_input = self._sanitize_input(user_input) if user_input else ""
        clean_bot_response = self._sanitize_input(bot_response) if bot_response else ""

        history_item = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": self.current_mode,
            "user": clean_user_input,
            "bot": clean_bot_response
        }
        self.history.append(history_item)

        # Auto-save to file if enabled
        if self.config.get("auto_save_history", False):
            self._save_history_to_file()

    def _save_history_to_file(self):
        """Save history to file."""
        history_file = self.config.get("history_file")
        if not history_file:
            return

        try:
            os.makedirs(os.path.dirname(history_file), exist_ok=True)

            # Load existing history
            existing_history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    existing_history = json.load(f)

            # Append new history
            existing_history.extend(self.history)

            # Save back to file
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(existing_history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self._print_colored(f"Warning: Could not save history: {e}", "warning")

    def _process_user_input(self, user_input: str) -> Optional[str]:
        """Process user input and get response from appropriate agent with session memory."""
        try:
            # Ensure input is clean before processing (additional safety layer)
            clean_input = self._sanitize_input(user_input)

            # Update session memory with user input
            if self.session_id and self.session_id in self.chat_memory:
                session_data = self.chat_memory[self.session_id]
                session_data["messages"].append({
                    "role": "user",
                    "content": clean_input,
                    "timestamp": datetime.now().isoformat(),
                    "mode": self.current_mode
                })

            response_content = None

            if self.current_mode == "chat":
                # Use EntryAgent for chat mode
                if not self.entry_agent:
                    self._print_colored("Chat agent not initialized!", "error")
                    return None

                # Get chat history for context
                chat_history = []
                if self.session_id and self.session_id in self.chat_memory:
                    chat_history = self.chat_memory[self.session_id]["messages"]

                # Pass session context to agent using cleaned input
                response = self.entry_agent.run(
                    clean_input,
                    session_id=self.session_id,
                    chat_history=chat_history
                )

                if hasattr(response, 'content'):
                    response_content = response.content
                else:
                    response_content = str(response)

            elif self.current_mode == "debug":
                # Use CodeFixAgent for debug mode
                if not self.code_fix_agent:
                    self._print_colored("Debug agent not initialized!", "error")
                    return None

                result = self.code_fix_agent.fix_problem(clean_input)

                if result and result.get("success"):
                    response_content = f"Debug analysis completed:\n"
                    response_content += f"Analysis: {result.get('analysis', {}).get('result', 'N/A')}\n"
                    response_content += f"Plan: {result.get('plan', {})}\n"
                    response_content += f"Execution: {result.get('execution', {})}"
                else:
                    response_content = f"Debug failed: {result.get('error', 'Unknown error')}"

            # Update session memory with assistant response
            if response_content and self.session_id and self.session_id in self.chat_memory:
                session_data = self.chat_memory[self.session_id]
                session_data["messages"].append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().isoformat(),
                    "mode": self.current_mode
                })

            return response_content

        except Exception as e:
            self._print_colored(f"Error processing request: {e}", "error")
            return None

    def start_chat(self):
        """Start a new chat session - main entry point for xcoder command."""
        # Generate new session ID
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize session memory
        self.chat_memory[self.session_id] = {
            "messages": [],
            "context": {},
            "created_at": datetime.now().isoformat(),
            "mode_history": [self.current_mode]
        }

        self._print_colored(f"Starting new chat session: {self.session_id}", "system")

        # Start interactive mode
        self.run_interactive()

    def run_interactive(self):
        """Run the interactive CLI session."""
        self._print_banner()

        # Initialize agents
        if not self._initialize_agents():
            self._print_colored("Failed to start XCoder. Please check your setup.", "error")
            return

        self._print_colored("XCoder is ready! Type your message or use /help for commands.", "success")

        try:
            while True:
                # Show simple prompt
                prompt_color = self.config["theme"]["prompt_color"]
                raw_input = input(f"\n{prompt_color}xcoder >{Style.RESET_ALL} ").strip()

                # Sanitize input to handle problematic Unicode sequences
                user_input = self._sanitize_input(raw_input)

                if not user_input:
                    continue

                # Handle special commands
                if user_input.startswith("/"):
                    should_continue = self._handle_command(user_input)
                    if not should_continue:
                        break
                    continue

                # Process regular input
                self._print_colored("Processing...", "system")

                response = self._process_user_input(user_input)

                if response:
                    print(f"\n{Fore.WHITE}🤖 XCoder:{Style.RESET_ALL}")
                    print(f"{response}")

                    # Save to history
                    self._save_to_history(user_input, response)
                else:
                    self._print_colored("Sorry, I couldn't process your request.", "error")

        except KeyboardInterrupt:
            self._print_colored("\nSession interrupted by user. Goodbye! 👋", "warning")
        except Exception as e:
            self._print_colored(f"Unexpected error: {e}", "error")
        finally:
            self._save_config()
            if self.config.get("auto_save_history", False):
                self._save_history_to_file()


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="XCoder - Intelligent Coding Assistant CLI")
    parser.add_argument("--mode", choices=["chat", "debug"], default="chat",
                       help="Initial mode (default: chat)")

    args = parser.parse_args()

    cli = XCoderCLI()

    # Override config with command line arguments
    if args.mode:
        cli.current_mode = args.mode

    # Start chat session
    cli.start_chat()




if __name__ == "__main__":
    main()
