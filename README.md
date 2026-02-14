# XCoder - Intelligent Coding Assistant

XCoder is a powerful command-line interface (CLI) tool that provides intelligent coding assistance powered by AI. It supports both chat mode for general conversation and debug mode for complex code analysis and bug fixing.

## Features

- 🤖 **Dual Mode Operation**: Chat mode for general assistance and Debug mode for code fixing
- 🔧 **Interactive CLI**: Beautiful, colorful terminal interface
- 💬 **Conversation History**: Auto-save and replay previous sessions
- ⚙️ **Configurable**: Customizable model, server URL, and themes
- 🚀 **Easy Installation**: Simple setup with setuptools entry_points

## Installation

### Quick Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/xcoder.git
cd xcoder
```

2. Install in development mode:
```bash
pip install -e .
```

3. Start using xcoder:
```bash
xcoder
```

### Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install xcoder
pip install -e .

# Run xcoder
xcoder
```

## Usage

### Starting XCoder

Simply type `xcoder` in your terminal:

```bash
xcoder
```

### Command Line Options

```bash
xcoder --help                 # Show help
xcoder --version             # Show version
xcoder --mode chat           # Start in chat mode (default)
xcoder --mode debug          # Start in debug mode
xcoder --model qwen3:latest  # Specify model
xcoder --url http://localhost:11434  # Specify Ollama server URL
```

### Interactive Commands

Once XCoder is running, you can use these commands:

- `/chat` - Switch to chat mode
- `/debug` - Switch to debug mode
- `/status` - Show current session status
- `/config` - Display configuration
- `/history` - Show conversation history
- `/clear` - Clear screen
- `/help` - Show detailed help
- `/exit` - Exit XCoder

### Modes

#### Chat Mode 💬
- General conversation and simple tasks
- Powered by EntryAgent
- Supports file operations, web search, etc.

#### Debug Mode 🔧
- Complex code analysis and bug fixing
- Powered by CodeFixAgent
- Advanced planning and multi-step execution

## Configuration

XCoder creates a configuration directory at `~/.xcoder/`:

- `~/.xcoder/config.json` - Main configuration file
- `~/.xcoder/history.json` - Conversation history

### Example Configuration

```json
{
  "model_name": "qwen3:latest",
  "base_url": "http://localhost:11434",
  "auto_save_history": true,
  "history_file": "~/.xcoder/history.json",
  "theme": {
    "prompt_color": "\u001b[32m",
    "system_color": "\u001b[36m",
    "error_color": "\u001b[31m",
    "success_color": "\u001b[32m",
    "warning_color": "\u001b[33m"
  }
}
```

## Prerequisites

- **Python**: 3.8 or higher
- **AI Provider**: Either Ollama or ZhipuAI API access
- **Dependencies**: Listed in `requirements.txt`

## Configuration

### Environment Variables

XCoder supports multiple AI providers. Copy `.env` to configure your settings:

```bash
cp .env .env.local  # Create your local configuration
```

Edit `.env.local` with your configuration:

```bash
# LangSmith Configuration (optional, for tracing)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=xcoder
LANGSMITH_TRACING=true

# LLM Provider Configuration
# Options: ollama, zhipuai
LLM_PROVIDER=ollama

# Ollama Configuration (used when LLM_PROVIDER=ollama)
OLLAMA_MODEL=qwen3:latest
OLLAMA_BASE_URL=http://localhost:11434

# ZhipuAI Configuration (used when LLM_PROVIDER=zhipuai)
ZHIPUAI_API_KEY=your_zhipuai_api_key_here
ZHIPUAI_MODEL=glm-4.7-flash
```

### Setting up AI Providers

#### Option 1: Ollama (Local)
1. Install Ollama from [https://ollama.com](https://ollama.com)
2. Pull a model (e.g., `ollama pull qwen3:latest`)
3. Ensure Ollama is running (`ollama serve`)
4. Set `LLM_PROVIDER=ollama` in your `.env.local`

#### Option 2: ZhipuAI (Cloud)
1. Get an API key from [ZhipuAI](https://open.bigmodel.cn/)
2. Set `LLM_PROVIDER=zhipuai` in your `.env.local`
3. Add your API key to `ZHIPUAI_API_KEY`

## Project Structure

```
xcoder/
├── cli/                 # CLI interface
│   ├── __init__.py
│   └── xcoder_cli.py   # Main CLI implementation
├── core/               # Core functionality
│   ├── agents/         # AI agents
│   ├── llm/           # Language model clients
│   ├── tools/         # Tool implementations
│   └── utils/         # Utilities
├── example/           # Usage examples
├── workspace/         # Working directory
├── requirements.txt   # Dependencies
├── setup.py          # Package setup
├── __init__.py       # Package init
└── README.md         # This file
```

## Development

### Installing for Development

```bash
git clone https://github.com/your-username/xcoder.git
cd xcoder
pip install -e .
```

## Usage Examples

### Basic Chat
```
[CHAT] xcoder > What's the weather like?
[CHAT] xcoder > How do I read a file in Python?
```

### Code Debugging
```
[DEBUG] xcoder > Fix the error in my_script.py
[DEBUG] xcoder > Analyze and refactor the authentication module
```

### Command Usage
```
[CHAT] xcoder > /debug        # Switch to debug mode
[DEBUG] xcoder > /status      # Show session status
[DEBUG] xcoder > /history     # View conversation history
[DEBUG] xcoder > /exit        # Exit XCoder
```

### Legacy Usage Methods

You can still use the old methods if preferred:

#### Using run_xcoder.py
```bash
# Start chat mode
python run_xcoder.py

# Start debug mode
python run_xcoder.py --mode debug

# View help
python run_xcoder.py --help
```

#### Direct agent usage
```bash
python core/agents/entry_agent.py
```

#### Programmatic usage
```python
from core.agents.entry_agent import EntryAgent

# Create agent instance
agent = EntryAgent(
    model_name="qwen2.5:7b",
    base_url="http://localhost:11434"
)

# Single query
response = agent.run("What time is it?")
print(response)

# With chat history
from langchain_core.messages import HumanMessage, AIMessage

chat_history = [
    HumanMessage(content="Hello"),
    AIMessage(content="Hello! How can I help you?")
]

response = agent.run("Calculate 123 + 456", chat_history)
print(response)
```

## Available Tools

1. **get_current_time**: Get current time and date
2. **calculate_math**: Safely calculate mathematical expressions
3. **get_weather_info**: Get city weather information (simulated)
4. **file_operations**: File read/write and directory listing
5. **web_search**: Web search functionality (simulated)

## Troubleshooting

### Common Issues

1. **Command not found**: Make sure you installed with `pip install -e .`
2. **Agent initialization failed**: Check if Ollama is running and model is available
3. **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)

### Getting Help

- Use `xcoder --help` for command line options
- Use `/help` within XCoder for interactive commands
- Check configuration with `/config` command

## License

MIT License - see LICENSE file for details.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Submit a Pull Request

## Community

- 🐛 [Report Issues](https://github.com/your-username/xcoder/issues)
- 💡 [Feature Requests](https://github.com/your-username/xcoder/issues)
- 📖 [Documentation](https://github.com/your-username/xcoder/wiki)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Security

If you discover a security vulnerability, please see our [Security Policy](SECURITY.md) for reporting instructions.
