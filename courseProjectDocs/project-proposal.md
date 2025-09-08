# Project Proposal & Setup

## Team

- [**AJ**](https://github.com/ajbarea)
- [**Connor**](https://github.com/cwo3990)
- [**Kemoy**](https://github.com/kemoycampbell)

## Project Overview

**Project**: MkDocs - Project documentation with Markdown  
**Language**: Python  

MkDocs is a fast and simple static site generator specifically designed for building project documentation. It transforms Markdown source files into HTML documentation sites using a single YAML configuration file. The project has gained wide use in the open-source community due to its simplicity and focus on documentation workflows.

### What MkDocs Does

MkDocs serves as a documentation build tool that:

- Converts Markdown files into static HTML documentation websites
- Provides built-in themes (mkdocs, readthedocs) and supports third-party themes
- Includes a development server with live-reload for real-time preview
- Supports plugins and Markdown extensions for enhanced functionality
- Enables easy deployment to various hosting platforms (GitHub Pages, S3, etc.)
- Focuses on developer-friendly documentation workflows

### Why We Chose MkDocs

- **Simple & Accessible**: MkDocs uses Python and Markdown, making it easy for our team to start quickly.
- **Active Community**: Regular updates and strong support ensure reliability and growth.
- **Team-Friendly Workflow**: GitHub integration and one-command deployment simplify collaboration.
- **Focused Purpose**: Its clear scope as a documentation generator makes it ideal for a manageable team project.

## Key Quality Attributes

### Performance

MkDocs prioritizes fast build times for documentation sites

### Usability

Simple YAML configuration and Markdown-based authoring

### Extensibility

Plugin system and theme architecture allow customization

### Maintainability

Well-structured Python codebase with established patterns

## Testing Plans

### Overview

Testing is essential to ensure that MkDocs meets the quality attributes listed above.

### Existing Tests

#### Current Testing Framework

Currently, MkDocs uses the [unittest](https://docs.python.org/3/library/unittest.html) framework. The tests currently include both integration and unit tests, which cover the following components:

- config
- utils
- build
- plugin
- search
- cli
- localization
- livereload
- integration
- GitHub deployment
- theme

### Test Coverage

MkDocs currently has code coverage of 91% and is managed by [Codecov](https://app.codecov.io/github/mkdocs/mkdocs?branch=master).

### Team Project Testing Goals

- [ ] Understand the existing test cases and identify gaps and edge cases
- [ ] Add at least 5 unit tests for uncovered or edge-case logic
- [ ] Identify components that can benefit from mocking/stubbing
- [ ] Implement unit tests using mocks/stubs
- [ ] Implement and run mutation testing
- [ ] Implement static analysis to identify code smells and potential bugs, and implement at least 2 fixes
- [ ] Implement integration tests for at least 2 modules
- [ ] Create black-box system test cases covering the main flows
- [ ] Scan the codebase with security tools and fix the issues or report the findings
- [ ] Perform performance tests and document the results

---

## Reference

- [MkDocs Documentation](https://www.mkdocs.org/)
- [MkDocs on GitHub](https://github.com/mkdocs/mkdocs)
