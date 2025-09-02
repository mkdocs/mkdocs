from pathlib import Path
from dataclasses import dataclass
import sys
from typing import Iterator


@dataclass
class CodeMetrics:
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0


def scan_python_file(file_path: Path) -> CodeMetrics:
    metrics = CodeMetrics()
    in_multiline_string = False
    multiline_delimiter = None

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                print("line #" + str(metrics.total_lines + 1) + ": " + line.strip())
                metrics.total_lines += 1
                stripped = line.strip()

                if not stripped:
                    metrics.blank_lines += 1
                    continue

                if in_multiline_string:
                    metrics.comment_lines += 1
                    if multiline_delimiter is not None and multiline_delimiter in stripped:
                        delimiter_count = stripped.count(multiline_delimiter)
                        if delimiter_count % 2 == 1:  # Odd count means it closes
                            in_multiline_string = False
                            multiline_delimiter = None
                    continue

                if stripped.startswith('"""') or stripped.startswith("'''"):
                    metrics.comment_lines += 1
                    if stripped.startswith('"""'):
                        delimiter = '"""'
                    else:
                        delimiter = "'''"

                    delimiter_count = stripped.count(delimiter)
                    if delimiter_count == 1:  # Opening but not closing on same line
                        in_multiline_string = True
                        multiline_delimiter = delimiter
                    # If count is 2, it's a single-line docstring, already counted
                    continue

                # Single-line comments
                if stripped.startswith('#'):
                    metrics.comment_lines += 1
                else:
                    metrics.code_lines += 1

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return metrics


def find_python_files(root_dir: Path) -> Iterator[Path]:
    return root_dir.rglob("*.py")


def scan_codebase(mkdocs_path: str = ".") -> CodeMetrics:
    root = Path(mkdocs_path)
    total_metrics = CodeMetrics()
    file_count = 0

    print(f"Scanning MkDocs codebase at: {root.absolute()}")

    for py_file in find_python_files(root):
        if any(
            part in py_file.parts
            for part in ['.git', '__pycache__', '.pytest_cache', 'build', 'dist']
        ):
            continue

        file_metrics = scan_python_file(py_file)
        total_metrics.total_lines += file_metrics.total_lines
        total_metrics.code_lines += file_metrics.code_lines
        total_metrics.comment_lines += file_metrics.comment_lines
        total_metrics.blank_lines += file_metrics.blank_lines
        file_count += 1

    print(f"\nScanned {file_count} Python files")
    print(f"Total lines: {total_metrics.total_lines}")
    print(f"Code lines: {total_metrics.code_lines}")
    print(f"Comment lines: {total_metrics.comment_lines}")
    print(f"Blank lines: {total_metrics.blank_lines}")

    return total_metrics


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not Path(path).exists():
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)

    metrics = scan_codebase(path)
