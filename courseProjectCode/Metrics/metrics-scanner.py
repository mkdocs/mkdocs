import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Tuple

import requests

"""Python source code metrics scanner with code coverage integration.

Analyzes Python codebases to count lines (total, code, comment, blank) and
integrates with external coverage APIs to provide comprehensive code quality metrics.
Generates detailed Markdown reports for maintainability analysis.

Example Usage:
    python3 courseProjectCode/Metrics/metrics-scanner.py
    python courseProjectCode/Metrics/metrics-scanner.py /path/to/codebase
"""

CODE_COVERAGE_DIRECTORY_DEPTH = 500
SONARQUBE_API_URL = "https://api.codecov.io/api/v2/github/mkdocs/repos/mkdocs/report/tree?depth="


def load_metrics_yaml() -> dict:
    """Load configuration from metrics.yaml file.

    Returns:
        dict: Configuration containing API token and exclude paths.
    """
    import yaml

    with open("courseProjectCode/Metrics/metrics.yaml", 'r') as f:
        return yaml.safe_load(f)


def fetch_code_coverage_data(token: str, depth: int = CODE_COVERAGE_DIRECTORY_DEPTH) -> dict:
    """Fetch code coverage data from external API.

    Args:
        token: API authentication token.
        depth: Directory depth limit for coverage analysis.

    Returns:
        dict: Coverage data structure or empty dict if fetch fails.
    """

    try:
        headers = {"accept": "application/json", "authorization": f"Bearer {token}"}
        response = requests.get(f"{SONARQUBE_API_URL}{depth}", headers=headers)
        response.raise_for_status()
        return response.json()[0]
    except requests.RequestException as e:
        print(f"Error fetching code coverage data: {e}")
        return {}


def coverage_get_node_stats(node: dict) -> Tuple[str, int, int, int, float]:
    """Extract statistics from a coverage node.

    Args:
        node: Coverage node dictionary from API response.

    Returns:
        Tuple containing: (name, total_lines, lines_tested, misses, coverage_percentage)
    """
    if not node:
        return '', 0, 0, 0, 0.0

    name = node.get("name", "")
    total_lines = node.get("lines", 0)
    lines_test = node.get("hits", 0)
    misses = node.get("misses", 0)
    coverage = node.get("coverage", 0.0)

    return name, total_lines, lines_test, misses, coverage


def coverage_nodes_helper_rec(node: dict, header_level: int = 3) -> str:
    """Recursively generate markdown for coverage nodes.

    Processes coverage data hierarchically, creating markdown sections for
    directories and files with their respective coverage statistics.

    Args:
        node: Coverage node to process.
        header_level: Markdown header level for this node.

    Returns:
        str: Formatted markdown content for the node and its children.
    """
    if not node:
        return ""

    md = []

    # Extract statistics for current node
    name, total_lines, lines_test, misses, coverage_percentage = coverage_get_node_stats(node)
    # Create markdown header for current node
    header = f"{'#' * header_level} {name}"
    md.append(header)

    # Add summary statistics line
    md.append(
        f"- **Total Lines:** {total_lines} | **Coverage:** {coverage_percentage:.2f}% | **Lines test:** {lines_test} | **Misses:** {misses}\n"
    )

    # Separate files and folders from node children
    files = []
    folders = []
    children = node.get("children", [])
    for child in children:
        # Files don't have children, folders do
        if "children" not in child:
            files.append(child)
        else:
            folders.append(child)

    # Generate markdown for files in this node
    if files:
        md.append("\t **Files:**")
        md.append("```python")
        for file in files:
            fname, ftotal_lines, fline_test, fmisses, fcoverage_percentage = (
                coverage_get_node_stats(file)
            )
            md.append(
                f"  - {fname} ({ftotal_lines} lines, {fcoverage_percentage:.2f}%, {fline_test} lines test, {fmisses} misses)"
            )
        md.append("```")
        md.append("")

    # Recursively process subdirectories
    for folder in folders:
        # Increment header level to show hierarchy
        folder_md = coverage_nodes_helper_rec(folder, header_level + 1)
        md.append(folder_md)

    return "\n".join(md)


def generate_coverage_markdown(coverage_data: Optional[dict]) -> str:
    """Generate complete markdown section for code coverage report.

    Args:
        coverage_data: Root coverage data from API.

    Returns:
        str: Complete markdown section with coverage analysis.
    """
    if not coverage_data:
        return "No coverage data available."

    md = []
    md.append("## Testability - Code Coverage Report")
    md.append("")

    nodes_md = coverage_nodes_helper_rec(coverage_data)
    md.append(nodes_md)
    return "\n".join(md)


@dataclass
class CodeMetrics:
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    sonarqube_code_coverage_data: Optional[dict] = None


def scan_python_file(file_path: Path) -> CodeMetrics:
    """Analyze a single Python file for line metrics.

    Counts total lines, code lines, comment lines (including docstrings),
    and blank lines while handling multiline strings correctly.

    Args:
        file_path: Path to the Python file to analyze.

    Returns:
        CodeMetrics: Object containing all line count metrics for the file.
    """
    metrics = CodeMetrics()
    in_multiline_string = False
    multiline_delimiter = None

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                metrics.total_lines += 1
                stripped = line.strip()

                if not stripped:
                    metrics.blank_lines += 1
                    continue

                if in_multiline_string:
                    metrics.comment_lines += 1
                    if multiline_delimiter is not None and multiline_delimiter in stripped:
                        delimiter_count = stripped.count(multiline_delimiter)
                        if delimiter_count % 2 == 1:
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
                    if delimiter_count == 1:
                        in_multiline_string = True
                        multiline_delimiter = delimiter
                    continue

                if stripped.startswith('#'):
                    metrics.comment_lines += 1
                else:
                    metrics.code_lines += 1

    except Exception as e:
        # Handle file reading errors gracefully
        print(f"Error reading {file_path}: {e}")

    return metrics


def find_python_files(root_dir: Path) -> Iterator[Path]:
    """Recursively discover all Python files in directory tree.

    Args:
        root_dir: Root directory to search from.

    Returns:
        Iterator[Path]: Generator yielding Path objects for Python files.
    """
    return root_dir.rglob("*.py")


def scan_codebase(exclude_paths: list[str], mkdocs_path: str = ".") -> Tuple[CodeMetrics, int]:
    """Scan entire codebase and aggregate metrics from all Python files.

    Recursively analyzes all Python files in the given path, excluding
    specified directories, and aggregates line count statistics.

    Args:
        exclude_paths: List of directory names to exclude from scanning.
        mkdocs_path: Root path to scan (defaults to current directory).

    Returns:
        Tuple[CodeMetrics, int]: Aggregated metrics and count of files scanned.
    """
    root = Path(mkdocs_path)
    total_metrics = CodeMetrics()
    file_count = 0

    print(f"Scanning MkDocs codebase at: {root.absolute()}")

    for py_file in find_python_files(root):
        if any(part in py_file.parts for part in exclude_paths):
            continue

        file_metrics = scan_python_file(py_file)
        total_metrics.total_lines += file_metrics.total_lines
        total_metrics.code_lines += file_metrics.code_lines
        total_metrics.comment_lines += file_metrics.comment_lines
        total_metrics.blank_lines += file_metrics.blank_lines
        file_count += 1

    print(f"\nScanned {file_count} Python files")

    return total_metrics, file_count


def render_markdown_report(metrics: CodeMetrics, scanned_path: str, file_count: int) -> str:
    """Generate comprehensive Markdown report from collected metrics.

    Creates a detailed report including line statistics, ratios, comment density,
    and integrated code coverage data.

    Args:
        metrics: Aggregated code metrics data.
        scanned_path: Path that was analyzed.
        file_count: Number of files that were scanned.

    Returns:
        str: Complete Markdown report content.
    """
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md = []
    md.append("# MkDocs Python Code Metrics")
    md.append("## Maintainability - Source Code Metrics")
    md.append("")
    md.append(f"**Scanned path:** `{scanned_path}`")
    md.append("")
    md.append(f"**Generated:** {now}")
    md.append("")
    md.append("### Summary")
    md.append("")
    md.append(f"- Python files scanned: **{file_count}**")
    md.append(f"- Total lines: **{metrics.total_lines}**")
    md.append(f"- Code lines: **{metrics.code_lines}**")
    md.append(f"- Comment lines: **{metrics.comment_lines}**")
    md.append(f"- Blank lines: **{metrics.blank_lines}**")
    md.append("")
    md.append("### Ratios")
    md.append("")
    try:
        code_percentage = (
            metrics.code_lines / metrics.total_lines * 100 if metrics.total_lines else 0
        )
        comment_percentage = (
            metrics.comment_lines / metrics.total_lines * 100 if metrics.total_lines else 0
        )
        blank_percentage = (
            metrics.blank_lines / metrics.total_lines * 100 if metrics.total_lines else 0
        )
    except Exception:
        code_percentage = comment_percentage = blank_percentage = 0

    # Calculate comment density (comments per line of code)
    try:
        comment_density = metrics.comment_lines / metrics.code_lines if metrics.code_lines else 0
    except Exception:
        comment_density = 0

    md.append(f"- Code: **{metrics.code_lines}** ({code_percentage:.1f}%)")
    md.append(f"- Comments: **{metrics.comment_lines}** ({comment_percentage:.1f}%)")
    md.append(f"- Blank: **{metrics.blank_lines}** ({blank_percentage:.1f}%)")
    md.append(f"- Comment density: **{comment_density:.3f}** ({comment_density*100:.1f}%)")

    # Append code coverage section to report
    coverage_md = generate_coverage_markdown(metrics.sonarqube_code_coverage_data)
    md.append(coverage_md)
    return "\n".join(md)


def write_markdown_report(output_path: Path, content: str) -> None:
    """Write markdown content to file, creating directories as needed.

    Args:
        output_path: Target file path for the report.
        content: Markdown content to write.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not Path(path).exists():
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)

    # Load configuration from YAML file
    metrics_config = load_metrics_yaml()
    token = metrics_config.get("token", "")
    exclude_paths = metrics_config.get("exclude_paths", [])

    metrics, file_count = scan_codebase(exclude_paths, path)
    # Fetch and attach code coverage data to metrics
    metrics.sonarqube_code_coverage_data = fetch_code_coverage_data(token)

    # Write markdown report
    report = render_markdown_report(metrics, scanned_path=path, file_count=file_count)
    output_file = Path("courseProjectCode/Metrics") / "mkdocs_metrics.md"
    write_markdown_report(output_file, report)
    print(f"Markdown report: {output_file.absolute()}")
