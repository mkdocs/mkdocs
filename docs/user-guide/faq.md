# Frequently Asked Questions

FAQ of common questions and problems

---

## Search has disappeared

(copied from the [plugins][plugins] documentation)
If the `plugins` config setting is defined in the `mkdocs.yml` config file, then
any defaults (such as `search`) are ignored and you need to explicitly re-enable
the defaults if you would like to continue using them:

```yaml
plugins:
    - search
    - your_other_plugin
```

[plugins]: /user-guide/configuration/#plugins
