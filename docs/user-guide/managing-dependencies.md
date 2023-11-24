# Managing Dependencies

---

<p></p>

In order to build an MkDocs site, you need to first [install](installation.md) MkDocs itself - that is the minimum.  
Then if you want to add [plugins](https://www.mkdocs.org/dev-guide/plugins/) or use a different [theme](https://www.mkdocs.org/user-guide/choosing-your-theme/#third-party-themes), you need to install those as well.

All of these are Python-based projects, so Python's package manager [`pip`](https://pip.pypa.io/) is used to install everything.

For example you found the ["macros" plugin](https://github.com/fralau/mkdocs_macros_plugin), and the instructions tell you to install its package by running this command:

```console
$ pip install mkdocs-macros-plugin
```

and then adding this to mkdocs.yml:

```yaml
plugins:
  - macros
```

At which point you will be ready to run `mkdocs build` and the plugin will kick in.

WARNING: Installing an MkDocs plugin or theme means installing a Python package and executing any code that the author has put in there. So, exercise the usual caution; there's no attempt at sandboxing.

The [official catalog of third-party projects and plugins](https://github.com/mkdocs/best-of-mkdocs) also lists both halves of this instruction upfront. The name of the MkDocs plugin doesn't have to match the name of the Python package that it's provided by, so you'll need to know both.

## Best practices

The above covers the basics, but there are several more things that are good to be aware of.

You can directly skip to the [next section](#recommended-config-for-hatch-project-manager), because it suggests an easy configuration that satisfies all the best-practice advice. But if you're curious about the reasoning, read on.

### Possible issues with dependencies

*   _Just running a bare `pip install` puts the packages into the global directory of the current user_

    If you are doing several separate things with Python, eventually it will become a mess - when working on one project you may upgrade a package and all of its dependencies, but then another project may become broken from that, and you may not even realize why.

    This is why it is very commonly **advised** to use [virtual environments](https://docs.python.org/3/tutorial/venv.html) - a special directory is created adjacent to the current project, and all the installed Python packages are confined to it. In the example [below](#recommended-config-for-hatch-project-manager), the project manager tool Hatch will be recommended instead of using virtualenvs directly, because it manages them in a particularly convenient way.

*   _Others will not know which packages to install_

    Given the sources for an MkDocs site, another person (or an automation setup) have to figure out which Python packages you installed to get all of the same plugins.

    The **advice** historically has been to document the list of dependencies in a `requirements.txt` file, so that someone else can install the same with `pip install -r requirements.txt`.

    But there is also a **new option**: as long as only public plugins from [the catalog](https://github.com/mkdocs/catalog) are used, the names of necessary packages can be inferred just by running [`mkdocs get-deps` - see more info there](https://github.com/mkdocs/get-deps).

*   _Others may get different versions of the packages_

    An MkDocs site may be using a lot of different plugins, and newer versions of those plugins may have changed behaviors or feature sets. Someone else, despite trying to get the same packages as you, may get a newer version of the package and they will not understand why the built site looks differently to them than was originally intended. This can become even worse if several people may be _deploying_ the site.

    That is why you **should** always prefer to record the exact versions of each package, and then consistently install the same versions, until you decide to upgrade. You can take a snapshot of the versions by running `pip freeze`, or even better, [`pip-compile`](https://github.com/jazzband/pip-tools) on the requirements file. This pinned `requirements.txt` file should be checked into your repository, then others can install the same versions by pointing `pip` at it.

## Recommended config for [Hatch](https://hatch.pypa.io/) project manager

To make use of this, you will need to [install Hatch](https://hatch.pypa.io/latest/install/#pip). Ideally in an isolated way with **`pipx install hatch`** (after [installing `pipx`](https://pypa.github.io/pipx/installation/)), or just `pip install hatch` as a more well-known way.

Then let's proceed to choose and add a configuration file for it.

You can change the selections below if you have a strong preference, but the default selection is best.

<div class="configurator">
<hr>
<input type="checkbox" checked id="label-auto-deps"> <label for="label-auto-deps">I want to automatically infer Python dependencies of the MkDocs site</label>
<br>
<input type="checkbox" checked id="label-pin-deps"> <label for="label-pin-deps">I want to pin my dependencies</label>
<br>
<span>I want to configure the Hatch environment:</span>
<span><input type="radio" name="is-pyproject" checked id="label-is-pyproject-1"> <label for="label-is-pyproject-1">as its own config file</label></span> /
<input type="radio" name="is-pyproject" id="label-is-pyproject-2"> <label for="label-is-pyproject-2">with an existing Python project</label>
<br>
<hr>

{% for auto_deps in true, false %}
{% for pin_deps in false, true %}
{% for is_pyproject in false, true %}

<div class="{% for cls in [auto_deps, pin_deps, is_pyproject] %}{% if cls %}c{{loop.index}} {% endif %}{% endfor %}">

{% if auto_deps and not pin_deps %}
<p>(Note: this selection is not recommended, as it's too implicit/volatile)</p>
{% endif %}

<p>Add this content to your repository as <code>{% if is_pyproject %}pyproject.toml{% else %}hatch.toml{% endif %}</code>:</p>

```toml
{%- if auto_deps or pin_deps %}
[{% if is_pyproject %}tool.hatch.{% endif %}env]
{%- if not auto_deps %}
requires = ["hatch-pip-compile"]
{%- elif not pin_deps %}
requires = ["hatch-mkdocs"]
{%- else %}
requires = [
    "hatch-mkdocs",
    "hatch-pip-compile",
]
{%- endif %}
{% endif %}
{%- if auto_deps %}
[{% if is_pyproject %}tool.hatch.{% endif %}env.collectors.mkdocs.docs]
path = "mkdocs.yml"
{% endif %}
{%- if pin_deps or not auto_deps %}
[{% if is_pyproject %}tool.hatch.{% endif %}envs.docs]
{%- if pin_deps %}
type = "pip-compile"
pip-compile-hashes = false
{%- endif -%}
{%- if not auto_deps %}
detached = true
dependencies = [
    "mkdocs",
    ...
]

[{% if is_pyproject %}tool.hatch.{% endif %}envs.docs.scripts]
build = "mkdocs build -f mkdocs.yml {args}"
serve = "mkdocs serve -f mkdocs.yml {args}"
gh-deploy = "mkdocs gh-deploy -f mkdocs.yml {args}"
{%- endif %}
{%- endif %}
```

{%- if not auto_deps %}
</p>Make sure to write out the actual package dependencies instead of "..." above.</p>
{%- endif %}

<p>Having done this, we can now just run the following command to build the MkDocs site, also installing all dependencies into a new environment if run for the first time:</p>

```console
$ hatch run docs:build
Creating environment: docs
Checking dependencies
Syncing dependencies
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: site
INFO    -  Documentation built in 0.03 seconds
```

{%- if pin_deps %}
<p>The dependencies are resolved to fixed versions recursively and written to the file <code>requirements/requirements-docs.txt</code>. You should check this file into your repository. That way any other user or machine building this site will get the exact same dependencies. In fact, if someone does not have Hatch installed, they can still benefit from this setup - just pass the requirements.txt file to <code>pip install</code>.</p>

<p>This is achieved through the Hatch plugin <a href="https://github.com/juftin/hatch-pip-compile">hatch-pip-compile</a> - see details and configuration options there.</p>

<p><a href="https://github.com/mkdocs/mkdocs/blob/master/requirements/requirements-docs.txt">See a real example of this requirements pin file.</a></p>

<p>If at any point you want to upgrade the pinned versions of dependencies, you can just delete this requirements file and re-run the build:</p>

```console
$ rm requirements/requirements-docs.txt
$ hatch run docs:build
```

{%- else %}
<p>If at any point you want to make sure the dependencies are re-installed anew, you can just remove the environment, then re-run the build:</p>

```console
$ hatch env remove docs
$ hatch run docs:build
```

{%- endif %}

{%- if auto_deps %}
<p>The dependencies stay in sync with the <code>mkdocs.yml</code> file. Any time you add or remove a plugin from the config and build the site, the exact dependencies will be re-calculated and re-installed.</p>

{%- if not pin_deps %}
<p>To view the set of dependencies that gets inferred, you can run <code>hatch env show docs</code>.</p>
{%- endif %}

<p>This is achieved through the Hatch plugin <a href="https://github.com/mkdocs/hatch-mkdocs">hatch-mkdocs</a> - see more details there.</p>
{%- endif %}

</div>

{% endfor %}
{% endfor %}
{% endfor %}

</div>
