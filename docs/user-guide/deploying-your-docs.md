# Deploying your docs

A basic guide to deploying your docs to various hosting providers

---

## GitHub Pages

If you host the source code for a project on [GitHub], you can easily use
[GitHub Pages] to host the documentation for your project. There are two basic
types of GitHub Pages sites: [Project Pages] sites, and [User and Organization
Pages] sites. They are nearly identical but have some important differences,
which require a different work flow when deploying.

### Project Pages

Project Pages sites are simpler as the site files get deployed to a branch
within the project repository (`gh-pages` by default). After you `checkout` the
primary working branch (usually `main`) of the git repository where you
maintain the source documentation for your project, run the following command:

```sh
mkdocs gh-deploy
```

That's it! Behind the scenes, MkDocs will build your docs and use the
[ghp-import] tool to commit them to the `gh-pages` branch and push the
`gh-pages` branch to GitHub.

Use `mkdocs gh-deploy --help` to get a full list of options available for the
`gh-deploy` command.

Please note that you will not be able to review the built site before it is
deployed to GitHub. Instead, you may want to verify any changes you made by
using the `build` or `serve` commands and reviewing the built files locally
before running `gh-deploy`.

WARNING:
The site files in the `gh-pages` branch are **automatically generated** and
updated when using the `gh-deploy` script.  
As such, you should never make any changes to the site files of your GitHub
Pages site by hand. Doing so will cause you to lose these changes the next time
the `gh-deploy` script or command is called.

WARNING:
If there are untracked files or uncommitted work in the local repository where
`mkdocs gh-deploy` is run, these will be included in the deployed Pages site.

### Organization and User Pages

Organization and User GitHub Pages sites are not tied to a specific project,
and the site files are deployed to the `main` branch in a dedicated
repository named with the GitHub account name. Therefore, you will need working
copies of two repositories on your local system. For example, consider the
following file structure:

```text
my-project/
    mkdocs.yml
    docs/
orgname.github.io/
```

After making and verifying updates to the `my-project` repository, change
directories to the `orgname.github.io` repository and call the `mkdocs
gh-deploy` command from there:

```sh
cd ../orgname.github.io/
mkdocs gh-deploy --config-file ../my-project/mkdocs.yml --remote-branch main
```

Please note that you need to explicitly point to the `mkdocs.yml` configuration
file in the `my-project` folder, as it is now no longer located in your current
working directory.  
You will also need to specify the `main` branch as the branch the deploy
script should commit to.

NOTE:
You may override the default branch with the [remote_branch] setting in the
`mkdocs.yml` configuration file, but forgetting to change directories before
running the deploy script will commit to the `main` branch of `my-project`,
likely overwriting the contents of your precious project.

WARNING:
The site files in the `main` branch are **automatically generated** and updated
when using the `gh-deploy` script.  
As such, you should never make any changes to the site files of your GitHub
Pages site by hand. Doing so will cause you to lose these changes the next time
the `gh-deploy` script or command is called.

### Custom Domains

GitHub Pages includes support for using a [Custom Domain] for your site. In
addition to the steps documented by GitHub, you need to take one additional step
so that MkDocs will work with your custom domain. You need to add a `CNAME` file
to the root of your [docs_dir]. The file must contain a single bare domain or
subdomain on a single line (see MkDocs' own [CNAME file] as an example). You may
create the file manually, or use GitHub's web interface to set up the custom
domain (under Settings / Custom Domain). If you use the web interface, GitHub
will create the `CNAME` file for you and save it to the root of your "pages"
branch. So that the file does not get removed the next time you deploy, you need
to copy the file to your `docs_dir`. With the file properly included in your
`docs_dir`, MkDocs will include the file in your built site and push it to your
"pages" branch each time you run the `gh-deploy` command.

If you are having problems getting a custom domain to work, see GitHub's
documentation on [Troubleshooting custom domains].

[GitHub]: https://github.com/
[GitHub Pages]: https://pages.github.com/
[Project Pages]: https://help.github.com/articles/user-organization-and-project-pages/#project-pages-sites
[User and Organization Pages]: https://help.github.com/articles/user-organization-and-project-pages/#user-and-organization-pages-sites
[ghp-import]: https://github.com/davisp/ghp-import
[remote_branch]: ./configuration.md#remote_branch
[Custom Domain]: https://help.github.com/articles/adding-or-removing-a-custom-domain-for-your-github-pages-site
[docs_dir]: ./configuration.md#docs_dir
[CNAME file]: https://github.com/mkdocs/mkdocs/blob/master/docs/CNAME
[Troubleshooting custom domains]: https://help.github.com/articles/troubleshooting-custom-domains/

## Read the Docs

[Read the Docs][rtd] offers free documentation hosting. You can import your docs
using the Git version control system. Read the Docs supports MkDocs out-of-the-box.
Follow the [instructions] on their site to arrange the files in your repository properly,
create an account and point it at your publicly hosted repository. If properly
configured, your documentation will update each time you push commits to your
public repository.

[rtd]: https://readthedocs.org/
[instructions]: https://docs.readthedocs.io/en/stable/intro/getting-started-with-mkdocs.html

## Other Providers

Any hosting provider which can serve static files can be used to serve
documentation generated by MkDocs. While it would be impossible to document how
to upload the docs to every hosting provider out there, the following guidelines
should provide some general assistance.

When you build your site (using the `mkdocs build` command), all of the files
are written to the directory assigned to the [site_dir] configuration option
(defaults to `"site"`) in your `mkdocs.yaml` config file. Generally, you will
simply need to copy the contents of that directory to the root directory of your
hosting provider's server. Depending on your hosting provider's setup, you may
need to use a graphical or command line [ftp], [ssh] or [scp] client to transfer
the files.

For example, a typical set of commands from the command line might look
something like this:

```sh
mkdocs build
scp -r ./site user@host:/path/to/server/root
```

Of course, you will need to replace `user` with the username you have with your
hosting provider and `host` with the appropriate domain name. Additionally, you
will need to adjust the `/path/to/server/root` to match the configuration of
your hosts' file system.

[ftp]: https://en.wikipedia.org/wiki/File_Transfer_Protocol
[ssh]: https://en.wikipedia.org/wiki/Secure_Shell
[scp]: https://en.wikipedia.org/wiki/Secure_copy

See your host's documentation for specifics. You will likely want to search
their documentation for "ftp" or "uploading site".

## Local Files

Rather than hosting your documentation on a server, you may instead distribute
the files directly, which can then be viewed in a browser using the `file://`
scheme.

Note that, due to the security settings of all modern browsers, some things
will not work the same and some features may not work at all. In fact, a few
settings will need to be customized in very specific ways.

-   [site_url]:

    The `site_url` must be set to an empty string, which instructs MkDocs to
    build your site so that it will work with the `file://` scheme.

    ```yaml
    site_url: ""
    ```

-   [use_directory_urls]:

    Set `use_directory_urls` to `false`. Otherwise, internal links between
    pages will not work properly.

    ```yaml
    use_directory_urls: false
    ```

-   [search]:

    You will need to either disable the search plugin, or use a third-party
    search plugin which is specifically designed to work with the `file://`
    scheme. To disable all plugins, set the `plugins` setting to an empty list.

    ```yaml
    plugins: []
    ```

    If you have other plugins enabled, simply ensure that `search` is not
    included in the list.

When writing your documentation, it is imperative that all internal links use
relative URLs as [documented][internal links]. Remember, each reader of your
documentation will be using a different device and the files will likely be in a
different location on that device.

If you expect your documentation to be viewed off-line, you may also need to be
careful about which themes you choose. Many themes make use of CDNs for various
support files, which require a live Internet connection. You will need to choose
a theme which includes all support files directly in the theme.

When you build your site (using the `mkdocs build` command), all of the files
are written to the directory assigned to the [site_dir] configuration option
(defaults to `"site"`) in your `mkdocs.yaml` config file. Generally, you will
simply need to copy the contents of that directory and distribute it to your
readers. Alternatively, you may choose to use a third party tool to convert the
HTML files to some other documentation format.

## 404 Pages

When MkDocs builds the documentation it will include a 404.html file in the
[build directory][site_dir]. This file will be automatically used when
deploying to [GitHub](#github-pages) but only on a custom domain. Other web
servers may be configured to use it but the feature won't always be available.
See the documentation for your server of choice for more information.

[site_dir]: ./configuration.md#site_dir
[site_url]: ./configuration.md#site_url
[use_directory_urls]: ./configuration.md#use_directory_urls
[search]: ./configuration.md#search
[internal links]: ./writing-your-docs.md#internal-links
