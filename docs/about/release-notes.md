# Release Notes

---

## Upgrading

To upgrade MkDocs to the latest version, use pip:

    pip install -U mkdocs

You can determine your currently installed version using `pip freeze`:

    pip freeze | grep mkdocs

## 0.11.1 (2014-11-20)

* Bugfix: Fix a CSS wrapping issue with code highlighting in the ReadTheDocs
  theme. (#233)


## 0.11.0 (2014-11-18)

* Render 404.html files if they exist for the current theme (#194)
* Bugfix: Fix long nav bars, table rendering and code highlighting in MkDocs
  and ReadTheDocs themes (#225)
* Bugfix: Fix an issue with the google_analytics code. (#219)
* Bugfix: Remove `__pycache__` from the package tar. (#196)
* Bugfix: Fix markdown links that go to an anchor on the current page (#197)
* Bugfix: Don't add `prettyprint well` CSS classes to all HTML, only add it in
  the MkDocs theme (#183)
* Bugfix: Display section titles in the ReadTheDocs theme (#175)
* Bugfix: Use the polling observer in watchdog so rebuilding works on
  filesystems without inotify. (#184)
* Bugfix: Improve error output for common configuration related errors. (#176)


## 0.10.0 (2014-10-29)

* Added support for Python 3.3 and 3.4. (#103)
* Configurable Python-Markdown extensions with the config setting
  `markdown_extensions`. (#74)
* Added `mkdocs json` command to output your rendered
  documentation as json files. (#128)
* Added `--clean` switch to `build`, `json` and `gh-deploy` commands to
  remove stale files from the output directory (#157)
* Support multiple theme directories to allow replacement of
  individual templates rather than copying the full theme. (#129)
* Bugfix: Fix `<ul>` rendering in readthedocs theme. (#171)
* Bugfix: Improve the readthedocs theme on smaller displays. (#168)
* Bugfix: Relaxed required python package versions to avoid clashes. (#104)
* Bugfix: Fix issue rendering the table of contents with some configs. (#146)
* Bugfix: Fix path for embedded images in sub pages. (#138)
* Bugfix: Fix `use_directory_urls` config behaviour. (#63)
* Bugfix: Support `extra_javascript` and `extra_css` in all themes (#90)
* Bugfix: Fix path-handling under Windows. (#121)
* Bugfix: Fix the menu generation in the readthedocs theme. (#110)
* Bugfix: Fix the mkdocs command creation under Windows. (#122)
* Bugfix: Correctly handle external `extra_javascript` and `extra_css`. (#92)
* Bugfix: Fixed favicon support. (#87)

