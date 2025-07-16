# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiofiles",
#     "jedi",
#     "mcp",
# ]
# ///

import asyncio
import os

from .tools import (
    find_definition,
    find_definition_by_name,
    find_references,
    list_symbols,
    find_in_file,
    setup_codenav,
)


def main():
    # Set up project first
    print("Set up CodeNav")
    project_path = os.getcwd()
    python_exec = input("Python executable (optional, press Enter to skip): ").strip()

    result = asyncio.run(setup_codenav(project_path, python_exec if python_exec else None))

    while True:
        print("\nAvailable commands:")
        print("1. List symbols in file")
        print("2. Find definition of symbol at location")
        print("3. Find definition of symbol by name")
        print("4. Find references to symbol")
        print("5. Find symbol by name in file")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            file_path = input("File path: ").strip()

            try:
                result = asyncio.run(list_symbols(file_path))
            except Exception as e:
                print(f"Error: {e}")
                continue

            if result == "No results":
                print("No symbols found in file")
                continue

            print("\nSymbols:")
            for category, symbols in result.items():
                if symbols:
                    print(f"\n{category.title()}:")
                    for symbol in symbols:
                        print(f"  {symbol}")

        elif choice == "2":
            file_path = input("File path: ").strip()
            line = input("Line number: ").strip()
            column = input("Column number: ").strip()

            try:
                result = asyncio.run(find_definition(file_path, int(line), int(column)))
            except Exception as e:
                print(f"Error: {e}")
                continue

            if result == "No results":
                print("No symbol found at specified location")
                continue

            print("\nSymbol Information:")
            for info in result['symbol_info']:
                print(f"  Kind: {info['kind']}")
                print(f"  Name: {info['name']}")
                if info['full_name']:
                    print(f"  Full name: {info['full_name']}")
                if info['description']:
                    print(f"  Description: {info['description']}")
                if info['help_text']:
                    print(f"  Documentation: {info['help_text'][:200]}...")

        elif choice == "3":
            file_path = input("File path: ").strip()
            line = input("Line number: ").strip()
            symbol_name = input("Symbol name: ").strip()
            occurrence = input("Occurrence (default 0): ").strip()

            try:
                occurrence_int = int(occurrence) if occurrence else 0
                result = asyncio.run(find_definition_by_name(file_path, int(line), symbol_name, occurrence_int))
            except Exception as e:
                print(f"Error: {e}")
                continue

            if result == "No results":
                print(f"Symbol '{symbol_name}' not found on line {line}")
                continue

            print("\nSymbol Information:")
            for info in result['symbol_info']:
                print(f"  Kind: {info['kind']}")
                print(f"  Name: {info['name']}")
                if info['full_name']:
                    print(f"  Full name: {info['full_name']}")
                if info['description']:
                    print(f"  Description: {info['description']}")
                if info['help_text']:
                    print(f"  Documentation: {info['help_text'][:200]}...")

        elif choice == "4":
            file_path = input("File path: ").strip()
            line = input("Line number: ").strip()
            column = input("Column number: ").strip()

            try:
                result = asyncio.run(find_references(file_path, int(line), int(column)))
            except Exception as e:
                print(f"Error: {e}")
                continue

            if result == "No results":
                print("No references found")
                continue

            print("\nSymbol references:")
            for i, ref in enumerate(result, 1):
                print(f"\n{i}. {ref['file_path']}:{ref['line']}:{ref['column']}")
                print(f"   {ref['source_line'].strip()}")

        elif choice == "5":
            file_path = input("File path: ").strip()
            symbol_name = input("Symbol name: ").strip()

            try:
                result = asyncio.run(find_in_file(file_path, symbol_name))
            except Exception as e:
                print(f"Error: {e}")
                continue

            if result == "No results":
                print(f"Symbol '{symbol_name}' not found in {file_path}")
                continue

            print("\nSymbol occurrences:")
            for i, occurrence in enumerate(result, 1):
                print(f"\n{i}. Line {occurrence['line']}:{occurrence['column']} ({occurrence['kind']})")
                print(f"   {occurrence['source_line'].strip()}")

        elif choice == "6":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("Exiting")
