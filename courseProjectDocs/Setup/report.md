# Baseline Build & Test

## Overview

This document shows how to build the project and gives you a summary of the test suite, baseline coverage metrics, and observations.

## Building the Project

1.  Clone the project:

      ```bash
      git clone https://github.com/kemoycampbell/mkdocs-AJ_Connor_Kemoy
      ```

2.  Change directory into the project folder and create a virtual environment.
      In this example, we create a virtual environment called mkdocVenv:

      ```bash
      cd mkdocs-AJ_Connor_Kemoy && python3 -m venv mkdocVenv
      ```

3.  Activate the mkdocVenv environment.
      **The command depends on your operating system:**

      - Linux & MacOS

      ```bash
      source mkdocVenv/bin/activate
      ```

      - Windows

      ```bash
      source mkdocVenv/Scripts/activate
      ```

4.  The main tool used to coordinate development and run tests in MkDocs is Hatch (<https://hatch.pypa.io/>). Install it:

      ```bash
      pip install hatch
      ```

5.  Ensure that all requirements and dependencies are installed by running the check.
      This installs dependencies, runs style and lint checks, and runs unit and integration tests across all supported Python versions. It might take a while:

      ```bash
      hatch run all
      ```

## Environment Information

- **Operating System**: Windows 11 (MINGW64 bash terminal)
- **Python Version**: 3.10.11 (primary), 3.8+ (hatch virtual environments)
- **Package Manager**: pip, hatch
- **Test Framework**: pytest
- **Build Tool**: hatch

## Test Suite Summary

### Test Types Available

- **Unit Tests**: Core functionality testing across Python versions 3.8-3.12
- **Integration Tests**: End-to-end testing with theme builds and test projects
- **Linting**: Code style and formatting checks
- **Type Checking**: Static type analysis

### Test Execution Commands

- `hatch run test:test` - Unit tests only
- `hatch run integration:test` - Integration tests only
- `hatch run all` - Complete test suite (style, lint, unit, integration)
- `hatch run style:fix` - Auto-fix style issues

## Baseline Coverage Metrics

### Overall Coverage

- **Total Coverage**: 90.31%
- **Total Lines**: 3,747
- **Lines Covered**: 3,384
- **Lines Missed**: 363

### Coverage by Module

- **mkdocs/**: 90.31% (3,747 lines)
- **commands/**: 81.14% (350 lines)
- **config/**: 92.80% (1,055 lines)
- **contrib/search/**: 93.88% (196 lines)
- **livereload/**: 86.44% (236 lines)
- **structure/**: 94.21% (916 lines)
- **utils/**: 90.58% (467 lines)

### Areas Requiring Attention

1. **commands/serve.py**: Only 21.31% coverage (13/61 lines tested)
2. **utils/cache.py**: 0% coverage (0/11 lines tested)
3. **utils/filters.py**: 0% coverage (0/1 lines tested)

### Detailed Code Metrics (Custom Scanner Analysis)

The metrics breakdown comes from a custom scanner script in [courseProjectCode/Metrics/](../../courseProjectCode/Metrics/). The script scans the codebase and grabs the coverage report from CodeCov's API.

#### Code Summary

- Python files scanned: **66**
- Total lines: **19,617**
- Code lines: **13,585**
- Comment lines: **2,653**
- Blank lines: **3,379**

#### Ratios

- Code: **13,585** (69.3%)
- Comments: **2,653** (13.5%)
- Blank: **3,379** (17.2%)
- Comment density: **0.195** (19.5%)

#### Detailed File-by-File Coverage

##### mkdocs/

- **Total Lines:** 3,747 | **Coverage:** 90.31% | **Lines tested:** 3,384 | **Misses:** 363

**Files:**

```python
- __init__.py (1 lines, 100.00%, 1 lines test, 0 misses)
- __main__.py (185 lines, 83.78%, 155 lines test, 30 misses)
- exceptions.py (10 lines, 90.00%, 9 lines test, 1 misses)
- localization.py (47 lines, 95.74%, 45 lines test, 2 misses)
- plugins.py (196 lines, 80.10%, 157 lines test, 39 misses)
- theme.py (88 lines, 90.91%, 80 lines test, 8 misses)
```

##### commands/

- **Total Lines:** 350 | **Coverage:** 81.14% | **Lines tested:** 284 | **Misses:** 66

**Files:**

```python
- build.py (179 lines, 97.21%, 174 lines test, 5 misses)
- gh_deploy.py (84 lines, 88.10%, 74 lines test, 10 misses)
- new.py (26 lines, 88.46%, 23 lines test, 3 misses)
- serve.py (61 lines, 21.31%, 13 lines test, 48 misses)
```

##### config/

- **Total Lines:** 1,055 | **Coverage:** 92.80% | **Lines tested:** 979 | **Misses:** 76

**Files:**

```python
- __init__.py (2 lines, 100.00%, 2 lines test, 0 misses)
- base.py (214 lines, 91.12%, 195 lines test, 19 misses)
- config_options.py (726 lines, 92.42%, 671 lines test, 55 misses)
- defaults.py (113 lines, 98.23%, 111 lines test, 2 misses)
```

##### contrib/search/

- **Total Lines:** 196 | **Coverage:** 93.88% | **Lines tested:** 184 | **Misses:** 12

**Files:**

```python
- __init__.py (87 lines, 94.25%, 82 lines test, 5 misses)
- search_index.py (109 lines, 93.58%, 102 lines test, 7 misses)
```

##### livereload/

- **Total Lines:** 236 | **Coverage:** 86.44% | **Lines tested:** 204 | **Misses:** 32

**Files:**

```python
- __init__.py (236 lines, 86.44%, 204 lines test, 32 misses)
```

##### structure/

- **Total Lines:** 916 | **Coverage:** 94.21% | **Lines tested:** 863 | **Misses:** 53

**Files:**

```python
- __init__.py (25 lines, 92.00%, 23 lines test, 2 misses)
- files.py (330 lines, 90.61%, 299 lines test, 31 misses)
- nav.py (153 lines, 96.73%, 148 lines test, 5 misses)
- pages.py (361 lines, 95.84%, 346 lines test, 15 misses)
- toc.py (47 lines, 100.00%, 47 lines test, 0 misses)
```

##### utils/

- **Total Lines:** 467 | **Coverage:** 90.58% | **Lines tested:** 423 | **Misses:** 44

**Files:**

```python
- __init__.py (216 lines, 95.37%, 206 lines test, 10 misses)
- babel_stub.py (22 lines, 100.00%, 22 lines test, 0 misses)
- cache.py (11 lines, 0.00%, 0 lines test, 11 misses)
- filters.py (1 lines, 0.00%, 0 lines test, 1 misses)
- meta.py (38 lines, 100.00%, 38 lines test, 0 misses)
- rendering.py (63 lines, 90.48%, 57 lines test, 6 misses)
- templates.py (41 lines, 80.49%, 33 lines test, 8 misses)
- yaml.py (75 lines, 89.33%, 67 lines test, 8 misses)
```

## Test Results Summary

### Expected Test Count

- **Total Tests**: 725 tests across all Python versions
- **Python 3.8**: 721 passed, 4 skipped
- **Python 3.9**: 719 passed, 6 skipped
- **Python 3.10**: 721 passed, 4 skipped
- **Python 3.11**: 719 passed, 6 skipped
- **Python 3.12**: 721 passed, 4 skipped

### Known Platform Issues

- **PyPy Tests**: Skipped due to PyPy3 not being installed

### Test Performance

- **Typical Runtime**: 10-18 seconds per Python version
- **Total Suite Runtime**: ~5-10 minutes for all versions

## Observations

### Strengths

- High overall test coverage (90.31%)
- Comprehensive test suite covering multiple Python versions
- Well-structured modular testing approach
- Integration testing covers theme builds and real project scenarios

### Areas for Improvement

- Several utility modules have zero test coverage
- Serve command functionality is undertested

### Development Environment Readiness

- **Build Status**: ✅ Project builds successfully
- **Test Status**: ✅ Core tests pass
- **Coverage Status**: ✅ Good coverage baseline established
- **Documentation**: ✅ Comprehensive setup instructions available
