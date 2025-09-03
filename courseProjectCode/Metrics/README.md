# Overview
This document contains an automated metrics scanner that measures the maintainability and testability of the MkDocs source code.

## Maintainability
The script scans the source base and excludes the paths defined in the `metrics.yaml` exclude list. We measure the following:
- Lines of Code (LoC) per module
- Comments
- Comment density
- Total files
- Blank lines

## Testability
MkDocs uses SonarQube code coverage in its setup. We take advantage of this by leveraging the SonarQube API and parsing the coverage reports for each of the unit tests.

We are particularly interested in the percentage of coverage, total lines, total lines covered, and total line misses for each file. We display the results in a node and node-children format so that it is easy to understand.

# Generated Report
The generated report will be a Markdown file created by `metrics-scanner.py`.

## Dependencies
The dependencies are defined in `courseProjectCode/Metrics/requirements.txt`:
- requests
- pyyaml

## Getting Started

1. Install the dependencies:
```bash
pip install -r courseProjectCode/Metrics/requirements.txt
```

2. Copy `SAMPLE_metrics.yaml` to create `metrics.yaml`:
```bash
cp courseProjectCode/Metrics/SAMPLE_metrics.yaml courseProjectCode/Metrics/metrics.yaml
```

3. Generate a token for SonarQube by going to [SonarCloud](https://sonarcloud.io/login). Log in, then go to your account settings and generate a token key.

4. Copy the token key into `metrics.yaml`.

5. Run the report generator:
```bash
python courseProjectCode/Metrics/metrics-scanner.py
```
