# Requirements & Test Oracles

## Functional Requirements

1. The system shall build static HTML files from Markdown files. ([`README.md:20`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L20))
2. The system shall generate a deployable version of the site using the `build` command. ([`__main__.py:275-291`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L275-L291))
3. The system shall support theming to allow customization of site appearance. ([`README.md:22`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L22))
4. The system shall support plugins to extend functionality. ([`README.md:21`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L21))
5. The system shall provide search functionality to allow users to search through the site content. ([`pyproject.toml:87`](https://github.com/mkdocs/mkdocs/blob/master/pyproject.toml#L87))
6. The system shall provide a development server with live-reload functionality using the serve command. ([`serve.py:31-36`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/commands/serve.py#L31-L36))
7. The system shall support deployment to GitHub Pages using the gh-deploy command. ([`__main__.py:293-326`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L293-L326))
8. The system shall create new documentation projects using the new command. ([`__main__.py:359-366`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L359-L366))

## Non-Functional Requirements

1. The system shall require Python 3.8 or higher for compatibility. ([`pyproject.toml:34`](https://github.com/mkdocs/mkdocs/blob/master/pyproject.toml#L34))
2. The system shall support cross-platform operation (OS independent). ([`pyproject.toml:19`](https://github.com/mkdocs/mkdocs/blob/master/pyproject.toml#L19))
3. The system shall build documentation faster than comparable static site generators. ([`README.md:9`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L9))
4. The system shall be configured using a single YAML file for simplicity. ([`README.md:11`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L11))
5. The system shall provide error handling with strict mode to abort builds on warnings. ([`__main__.py:116`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L116))
6. The system shall support deployment to multiple hosting platforms (GitHub Pages, S3, etc.). ([`docs/index.md:80-83`](https://github.com/mkdocs/mkdocs/blob/master/docs/index.md?plain=1#L80-L83))

<!-- TODO: Update Test Oracles table with requirements (order doesn't matter) -->
## Example Test Oracles Table

Requirement ID | Requirement Description | Test Oracle (Expected Behavior)
-----------------------|-----------------------------------|---------------------------------------------
FR-1                   | The system shall ………..| After adding "Buy milk"................
FR-2                   | The system shal…. ……..| After deleting `"Buy milk".............
NFR-1                | The system shall………... | When…………..within 1 second.
FR-4                   | ……..                                |............

---

## Additional Research Notes

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

- MkDocs tests the codebase with the `unittest` framework to ensure that the code does what it is supposed to do, with 90% code coverage managed by [Codecov](https://app.codecov.io/github/mkdocs/mkdocs?branch=master).

### Maintainability

#### Modular Design and Software Engineering Best Practices

- The codebase appears to be well-designed and follows software engineering best practices such that the code is modular, each component focuses on its responsibilities, functions follow single responsibility, and there is good use of classes and OOP principles.

### CI/CD Pipeline

-   MkDocs makes extensive use of GitHub Actions for CI/CD to support the following operations:
    - Coding style fixes are enforced through `autofix.yml`.
    - All pull requests and pushes are tested for unit tests, integration tests, and build tests as defined in `ci.yml`.
    - New releases are automatically deployed to PyPI after successful tests and builds, as defined in `deploy-release.yml`.
    - Documentation updates are also automatically managed and published by `docs.yml`.
