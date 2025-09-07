# Requirements & Test Oracles

## Functional Requirements
- The system shall build static HTML files from Markdown files.
- The system shall generate a deployable version of the site using `build`.
- The system shall support theming.
- The system shall support plugins.
- The system should allow the user to search through the site


## Non-Functional Requirements
### Performance
- MkDocs is a fast static site generator
### Extensibility
#### Themes
- Users may supply their own theme by extending the system’s theme to serve their own themes rather than the built-ins.

#### Plugins
- Users may extend the system’s plugins to allow extra customization functionalities without modifying the core plugin code.

### Usability
#### CLI
- The CLI ships with intuitive commands such as `build`, which allows the user to generate Markdown to `.html` files, and `gh-deploy`, which deploys the Markdown to a `github.io` page format.
- The `serve` command provides a hot reload feature where users can see changes live as they type, instead of needing to refresh the page on each Markdown update.

### Testability
- MkDocs tests the codebase with the `unittest` framework to ensure that the code does what it is supposed to do, with 90% code coverage managed by Codecov.

### Maintainability
#### Modular Design and Software Engineering Best Practices
- The codebase appears to be well-designed and follows software engineering best practices such that the code is modular, each component focuses on its responsibilities, functions follow single responsibility, and there is good use of classes and OOP principles.

### CI/CD Pipeline
- MkDocs makes extensive use of GitHub Actions for CI/CD to support the following operations:
  - Coding style fixes are enforced through `autofix.yml`.
  - All pull requests and pushes are tested for unit tests, integration tests, and build tests as defined in `ci.yml`.
  - New releases are automatically deployed to PyPI after successful tests and builds, as defined in `deploy-release.yml`.
  - Documentation updates are also automatically managed and published by `docs.yml`.
