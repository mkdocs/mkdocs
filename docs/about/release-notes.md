# Release Notes

---

## Upgrading

To upgrade MkDocs to the latest version, use pip:

    pip install -U mkdocs

You can determine your currently installed version using `pip freeze`:

    pip freeze | grep mkdocs


## 0.10.X series

* Added support for Python 3.3 and 3.4. (#103)
* Configurable Python-Markdown extensions with the config setting
  `mardown_extensions`. (#74)
* Added `mkdocs json` command to output your rendered
  documentation as json files. (#128)
* Support multiple theme directories to allow replacement of
  individual templates rather than copying the full theme. (#129)
* Bugfix: Fix issue rendering the table of contents with some
  configs. (#146)
* Bugfix: Fix path for embeded images in sub pages. (#138)
* Bugfix: Fix `use_directory_urls` config behaviour. (#63)
* Bugfix: Add support for `extra_javascript` and `extra_css` in
  all themes. (#90)
* Bugfix: Fix path-handling under windows. (#121)
* Bugfix: Fix the menu generation in the readthedocstheme. (#110)
* Bugfix: Fix the mkdocs command creation under Windows. (#122)
* Bugfix: Correctly handle external files in `extra_javascript` and
  `extra_css`. (#92)
* Bugfix: Fixed favicon support. (#87)

