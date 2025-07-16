from pathlib import Path
from typing import Optional

import aiofiles
import jedi
from jedi.api.classes import Name

# Global variables to store current project environment
_current_project_path: Optional[str] = None
_current_python_executable_path: Optional[str] = None
_current_project: Optional[jedi.Project] = None


async def _create_script(file_path: str) -> jedi.Script:
    """Create Jedi script with project context for the given file."""
    # Raise error if no project is set
    if _current_project is None:
        raise RuntimeError("No project set. Use set_analysis_project() first.")

    # Handle relative paths by resolving against current project path
    if not Path(file_path).is_absolute():
        file_path_abs = Path(_current_project_path) / file_path
        file_path_abs = file_path_abs.resolve()
    else:
        file_path_abs = Path(file_path).resolve()

    # Read the file content asynchronously
    async with aiofiles.open(file_path_abs, 'r', encoding='utf-8') as f:
        source = await f.read()

    return jedi.Script(
        code=source,
        path=str(file_path_abs),
        project=_current_project,
    )


async def setup_codenav(project_path: str, python_executable_path: Optional[str] = None):
    """Configure the project environment for all code analysis operations."""
    global _current_project_path, _current_python_executable_path, _current_project

    # Verify the path exists
    project_path = str(Path(project_path).resolve())
    if not Path(project_path).exists():
        raise FileNotFoundError(f"Project directory path does not exist: {project_path}")

    # Verify python executable path if provided
    if python_executable_path:
        python_executable_path = str(Path(python_executable_path).resolve())
        if not Path(python_executable_path).exists():
            raise FileNotFoundError(f"Python executable path does not exist: {python_executable_path}")

    _current_project_path = project_path
    _current_python_executable_path = python_executable_path
    _current_project = jedi.Project(project_path, environment_path=python_executable_path)

    return "Success"


async def find_definition_by_name(file_path: str, line: int, symbol_name: str, occurrence: int = 0):
    """Get comprehensive analysis for a symbol."""
    # Create script to get access to the file content
    script = await _create_script(file_path)

    # Get the line content
    lines = script._code.splitlines()
    if line < 1 or line > len(lines):
        raise ValueError(f"Line {line} is out of range (file has {len(lines)} lines)")

    line_content = lines[line - 1]  # Convert to 0-based indexing

    # Find all occurrences of the symbol name in the line
    occurrences = []
    start = 0
    while True:
        pos = line_content.find(symbol_name, start)
        if pos == -1:
            break
        occurrences.append(pos)
        start = pos + 1

    # Check if symbol was found
    if not occurrences:
        raise ValueError(f"Symbol '{symbol_name}' not found on line {line}")

    # Check if occurrence index is valid
    if occurrence < 0 or occurrence >= len(occurrences):
        raise ValueError(f"Occurrence {occurrence} is out of range (found {len(occurrences)} occurrences of '{symbol_name}' on line {line})")

    # Get column position
    column = occurrences[occurrence] + 1

    # Delegate to the existing function
    return await find_definition(file_path, line, column)


async def find_definition(file_path: str, line: int, column: int):
    """Get detailed information for specific symbol by exact location."""
    script = await _create_script(file_path)

    # Get definitions without following imports to see the immediate import
    immediate_defs: list[Name] = script.goto(line=line, column=column-1, follow_imports=False)

    # Get definitions with following imports to see the source
    source_defs: list[Name] = script.goto(line=line, column=column-1, follow_imports=True)

    # Get help information
    help_info: list[Name] = script.help(line=line, column=column-1)

    # Get type information
    type_info: list[Name] = script.infer(line=line, column=column-1)

    result = {
        "symbol_info": [],
        "type_info": [],
        "signature_info": [],
        "import_location": None,
    }

    # Process help information
    for help_obj in help_info:
        doc_data = {
            "kind": help_obj.type,
            "name": help_obj.name,
            "full_name": help_obj.full_name,
            "description": help_obj.description,
            "help_text": getattr(help_obj, 'docstring', lambda: "")()[:5000],
        }
        result["symbol_info"].append(doc_data)

    # Process type information
    for type_obj in type_info:
        type_data = {
            "kind": type_obj.type,
            "name": type_obj.name,
            "full_name": type_obj.full_name,
            "module_name": type_obj.module_name,
            "file_path": str(type_obj.module_path) if type_obj.module_path else None,
            "line": type_obj.line,
            "column": type_obj.column + 1,
        }
        result["type_info"].append(type_data)

        # Try to get signature if it's callable
        signatures = type_obj.get_signatures()
        for sig in signatures:
            sig_data = {
                "name": sig.name,
                "params": [
                    {
                        "kind": param.kind.description,
                        "name": param.name,
                        "description": param.description,
                    }
                    for param in sig.params
                ],
            }
            result["signature_info"].append(sig_data)

    # Check if symbol appears to be defined in another file and add import info
    if (immediate_defs and source_defs and immediate_defs[0].module_path != source_defs[0].module_path):
        # Process immediate definition (the import statement)
        import_def = immediate_defs[0]
        import_data = {
            "file_path": str(import_def.module_path) if import_def.module_path else None,
            "line": import_def.line,
            "column": import_def.column + 1,
        }

        result["import_location"] = import_data

    # Check if any results were found
    has_results = any(result[key] for key in result)

    return result if has_results else "No results"


async def list_symbols(file_path: str):
    """List symbols in a file."""
    script = await _create_script(file_path)

    # Get all names defined in this file
    names = script.get_names(all_scopes=True, definitions=True, references=True)

    result = {
        "modules": [],
        "classes": [],
        "instances": [],
        "functions": [],
        "params": [],
        "paths": [],
        "keywords": [],
        "properties": [],
        "statements": [],
    }

    type_table = {
        "module": "modules",
        "class": "classes",
        "instance": "instances",
        "function": "functions",
        "param": "params",
        "path": "paths",
        "keyword": "keywords",
        "property": "properties",
        "statement": "statements",
    }

    for name in names:
        result[type_table[name.type]].append(name.name)

    # for each result key, unique and sort it
    for key in result:
        result[key] = sorted(set(result[key]))

    # Check if any results were found
    has_results = any(result[key] for key in result)

    return result if has_results else "No results"


async def find_references(file_path: str, line: int, column: int):
    """Find all references to a symbol across the entire project."""
    script = await _create_script(file_path)
    references = script.get_references(line=line, column=column-1, include_builtins=True)

    result = []

    for ref in references:
        ref_info = {
            "file_path": str(ref.module_path) if ref.module_path else None,
            "line": ref.line,
            "column": ref.column + 1,
            "source_line": ref.get_line_code(),
        }
        result.append(ref_info)

    return result if result else "No results"


async def find_in_file(file_path: str, symbol_name: str):
    """Search for symbol by name across entire file."""
    script = await _create_script(file_path)
    names = script.get_names(all_scopes=True, definitions=True, references=True)

    result = []

    for name in names:
        if name.name == symbol_name:
            usage_info = {
                "kind": name.type,
                "line": name.line,
                "column": name.column + 1,
                "source_line": name.get_line_code(),
            }
            result.append(usage_info)

    return result if result else "No results"
