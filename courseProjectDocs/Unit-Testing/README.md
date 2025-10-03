# How to Run Added Unit Tests

## Prerequisites

1.  Clone the project:

    ```bash
    git clone https://github.com/kemoycampbell/mkdocs-AJ_Connor_Kemoy
    ```

2.  Change directory into the project folder and create a virtual environment.
    In this example, create a virtual environment called mkdocVenv:

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

4.  Install Hatch (the main testing tool):

   ```bash
   pip install hatch
   ```

## Running the Edge Case Tests

To run only the newly added edge case tests in `courseProjectCode/Unit-Testing/test_edge_cases.py`:

```bash
python -m unittest courseProjectCode.Unit-Testing.test_edge_cases -v
```

### Expected Output

- **Total Tests**: 6 tests
- **Expected Results**: 6 passed, 0 failed
- **Runtime**: ~0.004 seconds

### Sample Output

```bash
test_build_datetime_with_source_date_epoch ... ok
test_build_datetime_without_source_date_epoch ... ok
test_build_timestamp_with_empty_pages ... ok
test_config_option_immutable_default ... ok
test_config_option_mutable_default_copy ... ok
test_config_option_set_on_non_config_object ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.004s

OK
```

## Running All Unit Tests

To run the complete test suite including the newly added tests:

```bash
hatch run test:test
```

### Expected Output

- **Total Tests**: 731 tests per Python version (baseline was 725)
- **Typical Results**: 725-727 passed, 4-6 skipped per version
- **Runtime**: ~10-18 seconds per Python version

## Reproducing Coverage Report

To generate a coverage report that includes the newly added tests:

```bash
python -m coverage run --source=mkdocs -m unittest discover -s mkdocs/tests -p "*_tests.py"
python -m coverage report
```

### Expected Coverage Metrics

- **Overall Coverage**: 95% (baseline was 90.31%)
- **Coverage Improvement**: +4.69%
- **Additional Tests**: 6 new edge case tests

To generate an HTML coverage report:

```bash
python -m coverage html
```

The HTML report will be generated in the `htmlcov/` directory.

## Notes

- The new tests target edge cases in `mkdocs/config/base.py` and `mkdocs/utils/__init__.py`
- Tests focus on mutable/immutable default handling, SOURCE_DATE_EPOCH environment variable, and error handling
- All tests use the unittest framework to maintain consistency with the existing MkDocs test suite
