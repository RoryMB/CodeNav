# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiofiles",
#     "jedi",
#     "mcp",
# ]
# ///

"""CodeNav - An MCP server for Python code navigation and analysis"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from .tools import (
    find_definition as find_definition_impl,
    find_definition_by_name as find_definition_by_name_impl,
    find_in_file as find_in_file_impl,
    find_references as find_references_impl,
    list_symbols as list_symbols_impl,
    setup_codenav as setup_codenav_impl,
)


# ===== INITIALIZATION =====

mcp = FastMCP("CodeNav")


# ===== TOOLS =====

@mcp.tool()
async def setup_codenav(project_path: str, python_executable_path: Optional[str] = None):
    """Configure CodeNav for all downstream operations.

    Sets up the working directory and Python virtual environment that all subsequent CodeNav tools will use.
    This must be called before using any other CodeNav tools.

    Args:
        project_path: Root directory path of the Python project to analyze, typically the cwd
        python_executable_path: Path to virtual environment Python interpreter (e.g., .venv/bin/python)
    """
    return await setup_codenav_impl(project_path, python_executable_path)


@mcp.tool()
async def find_definition_by_name(file_path: str, line: int, symbol_name: str, occurrence: int = 0):
    """Find the definition for a symbol, including type info, signatures, scope, and documentation.

    Locates definitions across the entire codebase and external libraries, including installed packages.
    Handles any Python file in the project or environment, including files from external libraries and installed packages.

    Args:
        file_path: Path to the Python file
        line: Line number where the symbol appears
        symbol_name: Name of the symbol to analyze
        occurrence: Which occurrence, if symbol_name appears multiple times on the line (default: 0 for first)
    """
    return await find_definition_by_name_impl(file_path, line, symbol_name, occurrence)


@mcp.tool()
async def find_definition(file_path: str, line: int, column: int):
    """Find the definition for a symbol, including type info, signatures, scope, and documentation.

    Locates definitions across the entire codebase and external libraries, including installed packages.
    Handles any Python file in the project or environment, including files from external libraries and installed packages.

    Use find_definition_by_name instead if you do not know the **exact** column where the symbol is located.

    Args:
        file_path: Path to the Python file
        line: Exact line number (use exactly as provided by other CodeNav tools)
        column: Exact column number (use exactly as provided by other CodeNav tools)
    """
    return await find_definition_impl(file_path, line, column)


@mcp.tool()
async def list_symbols(file_path: str):
    """List symbols in a file.

    Lists every named code element, organized by functions, classes, variables, imports, and other symbols.
    Handles any Python file in the project or environment, including files from external libraries and installed packages.

    Args:
        file_path: Path to the Python file
    """
    return await list_symbols_impl(file_path)


@mcp.tool()
async def find_references(file_path: str, line: int, column: int):
    """Find all references to a symbol across the entire project and external libraries.

    Locates all usages across the codebase and installed packages, including third-party libraries.
    Handles any Python file in the project or environment, including files from external libraries and installed packages.

    Args:
        file_path: Path to the Python file
        line: Exact line number (use exactly as provided by other CodeNav tools)
        column: Exact column number (use exactly as provided by other CodeNav tools)
    """
    return await find_references_impl(file_path, line, column)


@mcp.tool()
async def find_in_file(file_path: str, symbol_name: str):
    """Search for the exact line and column numbers where a symbol occurs across an entire file.

    Handles any Python file in the project or environment, including files from external libraries and installed packages.

    Args:
        file_path: Path to the Python file
        symbol_name: Name of the symbol to search for
    """
    return await find_in_file_impl(file_path, symbol_name)


def main():
    mcp.run()


if __name__ == '__main__':
    main()
