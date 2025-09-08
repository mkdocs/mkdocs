# Requirements & Test Oracles

## Functional Requirements

1. <a id="FR-1"></a> The system shall build static HTML files from Markdown files. ([`README.md:20`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L20))
2. <a id="FR-2"></a> The system shall generate a deployable version of the site using the `build` command. ([`__main__.py:275-291`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L275-L291))
3. <a id="FR-3"></a> The system shall support theming to allow customization of site appearance. ([`README.md:22`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L22))
4. <a id="FR-4"></a> The system shall support plugins to extend functionality. ([`README.md:21`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L21))
5. <a id="FR-5"></a> The system shall provide search functionality to allow users to search through the site content. ([`pyproject.toml:87`](https://github.com/mkdocs/mkdocs/blob/master/pyproject.toml#L87))
6. <a id="FR-6"></a> The system shall provide a development server with live-reload functionality using the serve command. ([`serve.py:31-36`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/commands/serve.py#L31-L36))
7. <a id="FR-7"></a> The system shall support deployment to GitHub Pages using the gh-deploy command. ([`__main__.py:293-326`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L293-L326))
8. <a id="FR-8"></a> The system shall create new documentation projects using the new command. ([`__main__.py:359-366`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L359-L366))
9. <a id="FR-9"></a> The system shall support configuration inheritance. ([`configuration.md:1142-1289`](https://github.com/mkdocs/mkdocs/blob/master/docs/user-guide/configuration.md?plain=1#L1142-L1289))
10. <a id="FR-10"></a> The system shall support hooks for one-off custom actions at specific points in the build process as a simpler alternative to plugins. ([`configuration.md:822-878`](https://github.com/mkdocs/mkdocs/blob/master/docs/user-guide/configuration.md?plain=1#L822-L878))

## Non-Functional Requirements

1. <a id="NFR-1"></a> The system shall require Python 3.8 or higher for compatibility. ([`pyproject.toml:34`](https://github.com/mkdocs/mkdocs/blob/master/pyproject.toml#L34))
2. <a id="NFR-2"></a> The system shall support cross-platform operation (OS independent). ([`pyproject.toml:19`](https://github.com/mkdocs/mkdocs/blob/master/pyproject.toml#L19))
3. <a id="NFR-3"></a> The system shall build documentation faster than comparable static site generators. ([`README.md:9`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L9))
4. <a id="NFR-4"></a> The system shall be configurable using a single YAML file for simplicity. ([`README.md:11`](https://github.com/mkdocs/mkdocs/blob/master/README.md?plain=1#L11))
5. <a id="NFR-5"></a> The system shall provide error handling with strict mode to abort builds on warnings. ([`__main__.py:116`](https://github.com/mkdocs/mkdocs/blob/master/mkdocs/__main__.py#L116))
6. <a id="NFR-6"></a> The system shall support deployment to multiple hosting platforms (GitHub Pages, S3, etc.). ([`docs/index.md:80-83`](https://github.com/mkdocs/mkdocs/blob/master/docs/index.md?plain=1#L80-L83))
7. <a id="NFR-7"></a> The system should allow organizations to manage multiple projects' documentation without redundant configurations as the number of projects increases. ([`configuration.md:1142-1289`](https://github.com/mkdocs/mkdocs/blob/master/docs/user-guide/configuration.md?plain=1#L1142-L1289))

## Test Oracles Table

Requirement ID | Requirement Description | Test Oracle (Expected Behavior)
-----------------------|-----------------------------------|---------------------------------------------
[FR-1](#FR-1)                   |  The system shall build static HTML files from Markdown files.| After running the `build` command, the `site` directory should contain a `.html` file for each corresponding `.md` file in the `docs` directory.
[FR-2](#FR-2)                  | The system shall generate a deployable version of the site using the `build` command.| After running the `build` command, a `site` directory should be created with the generated HTML files.
[FR-3](#FR-3)                  | The system shall support theming to allow customization of site appearance.| When the user specifies a theme in the `mkdocs.yml` configuration file, the generated HTML files should reflect the theme's styles and layout.
[FR-4](#FR-4)               | The system shall support plugins to extend functionality.| When a plugin is added to the `mkdocs.yml` configuration file, the plugin's functionality should be applied during the build process.
[FR-5](#FR-5)               | The system shall provide search functionality to allow users to search through the site content.| When the user includes the search plugin in the `mkdocs.yml` configuration file, a search box should appear on the generated site's nav bar, allowing users to search for content.
[FR-6](#FR-6)               | The system shall provide a development server with live-reload functionality using the serve command.| When the user runs the `serve` command, a local server should start, which should automatically refresh when changes are made to any of the markdown files.
[FR-7](#FR-7)               | The system shall support deployment to GitHub Pages using the `gh-deploy` command. | After running the `gh-deploy` command, the site should be published to the specified GitHub Pages repository/branch.
[FR-8](#FR-8)               | The system shall create new documentation projects using the `new` command. | After running the `new` command using the default options, the directory should contain a basic MkDocs project structure with a config file (`mkdocs.yml`) and a `docs` directory with a single markdown file (`index.md`).
[FR-9](#FR-9)               | The system shall support configuration inheritance. | When the `mkdocs.yml` file for a project inherits settings from a base configuration file, the resulting settings used by mkdocs should be the settings defined in the current project's `mkdocs.yml` and the settings from the base configuration that were not overridden by the current project's configuration.
[FR-10](#FR-10)               | The system shall support hooks for one-off custom actions at specific points in the build process as a simpler alternative to plugins. | When a hook file is defined in the `mkdocs.yml` configuration file, the specified hook file should be loaded as a plugin with all the defined hook functions as attributes.
[NFR-1](#NFR-1)                | The system shall require Python 3.8 or higher for compatibility. | When the user runs mkdocs, the system should work as intended without compatibility issues on Python 3.8 or higher.
[NFR-2](#NFR-2)                | The system shall support cross-platform operation (OS independent). | When the user runs mkdocs on different operating systems, the system should work as intended without noticable differences in behavior.
[NFR-3](#NFR-3)                | The system shall build documentation faster than comparable static site generators. | When the user runs the `build` command, the time taken to build the documentation should be less than that of comparable static site generators for the same set of markdown files.
[NFR-4](#NFR-4)                | The system shall be configurable using a single YAML file for simplicity. | When an mkdocs command is run, the resulting files and/or process should reflect the options specified in the configuration file.
[NFR-5](#NFR-5)                | The system shall provide error handling with strict mode to abort builds on warnings. | When the user runs the `build` command with strict mode enabled, the system should abort if any warnings are encountered during the build process.

---

## Additional Research Notes

### Performance

- MkDocs is a fast static site generator

### Extensibility

#### Themes

- Users may supply their own theme by extending the system’s theme to serve their own themes rather than the built-ins.

#### Plugins

- Users may extend the system’s plugins to allow extra customization functionalities without modifying the core plugin code.

#### Hooks
- Users may create their own hooks to allow one-off custom actions at specific points in the build process as a simpler alternative to plugins. 
- MkDocs treats a file containing hook functions as a plugin, and they eliminate the need to develop or install a full plugin for simple tasks.

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

### Scalability

#### Configuration Inheritance
- MkDocs allows organizations that manage multiple sites to define a single base configuration file that contains common settings shared across all projects via configuration inheritance. Each project can then have its own `mkdocs.yml` file that inherits from the base configuration and overrides or extends specific settings as needed. This approach reduces redundancy and simplifies management as the number of projects increases.
    - In order to take advantage of configuration inheritance, the markdown files must all use key/value syntax for defining configuration options.

