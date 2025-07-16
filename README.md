# CodeNav

An MCP (Model Context Protocol) server for Python code navigation and analysis. CodeNav provides agents with powerful tools to explore, understand, and analyze Python codebases via the Jedi language server.

## Available Tools

### Project Management

**`set_analysis_project`** - Configure project environment for analysis
- `project_path` (string): Root directory path of the Python project to analyze
- `python_executable_path` (string, optional): Path to specific Python interpreter

**`get_current_analysis_project`** - Get current project settings
- No arguments

### Symbol Analysis

**`find_definition_by_name`** - Analyze symbols by name and line number
- `file_path` (string): Path to the Python file
- `line` (integer): Line number where the symbol appears
- `symbol_name` (string): Name of the symbol to analyze
- `occurrence` (integer, optional): Which occurrence if name appears multiple times on line (default: 0)

**`find_definition`** - Get detailed symbol information by exact location
- `file_path` (string): Path to the Python file
- `line` (integer): Exact line number
- `column` (integer): Exact column number

**`list_symbols`** - List all symbols in a file by category
- `file_path` (string): Path to the Python file

### Code Exploration

**`find_references`** - Find all references to a symbol across the project
- `file_path` (string): Path to the Python file
- `line` (integer): Exact line number
- `column` (integer): Exact column number

**`find_in_file`** - Search for symbol usage within a specific file
- `file_path` (string): Path to the Python file
- `symbol_name` (string): Name of the symbol to search for

## Add to Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "CodeNav": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/RoryMB/CodeNav@main", "codenav"]
    }
  }
}
```

## Manual Use

### Command Line

Run this command to open an interactive menu with options to use the various tools:

```bash
uvx --from git+https://github.com/RoryMB/CodeNav@main codenav --cli
```

### Python Import

```python
import asyncio
from codenav import set_analysis_project, list_symbols_in_file, analyze_symbol_at_location

async def main():
    # Set up project
    await set_analysis_project("/path/to/your/project")
    
    # List symbols in a file
    symbols = await list_symbols_in_file("src/main.py")
    print(f"Functions: {symbols['functions']}")
    
    # Analyze a symbol
    result = await analyze_symbol_at_location("src/main.py", line=25, column=10)
    print(f"Symbol: {result}")

# Run the async function
asyncio.run(main())
```
