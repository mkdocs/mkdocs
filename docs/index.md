# MkDocs

Project documentation with&nbsp;Markdown.

---

## Overview

MkDocs is a **fast**, **simple** and **downright gorgeous** static site generator that's geared towards building project documentation. Documentation source files are written in Markdown, and configured with a single yaml configuration file.

---

**MkDocs is currently still in development.**

We're progressing quickly, but the documentation still needs filling in, and theres a few rough edges.  The 1.0 release is planned to arrive in the next few weeks.

---

#### Host anywhere.

Builds completely static HTML sites that you can host on GitHub pages, Amazon S3, or anywhere else you choose.

#### Great themes available.

There's a stack of good looking themes included by default. Choose from bootstrap, readthedocs, ghostwriter, or any of the 12 bootswatch themes.

#### Preview your site as you work.

The built-in devserver allows you to preview your documentation as your writing it. It will even auto-reload whenever you save any changes, so all you need to do to see your latest edits is refresh your browser.

#### Easy to customize.

Get your project documentation looking just the way you want it by customizing the theme.

#### Cross-reference your documentation.

Create richly cross-referenced documents, using the MkDocs interlinking syntax.

---

## Installation

Install using pip:

    pip install mkdocs

You should now have the `mkdocs` command installed on your system.  Run `mkdocs help` to check that everything worked okay.

    $ mkdocs help
    mkdocs [build|serve] {options}

---

## Getting started

In order to run, mkdocs requires a single configuration file named `mkdocs.yml` to exist in the current directory.

There are two required settings in the configuration file, `site_name`, and `pages`.  Let's create a simple configuration file for our new project `MkLorum`:

    site_name: 'MkLorum'
    pages:
    - ['index.md', 'Home']
    - ['about.md', 'About']

Your documentation source files should all exist in a single directory. By default this directory should be named `docs`.

    $ mkdir docs

Now we need some documentation. The markdown files in our `docs` directory should correspond with the entries in the configuration file, so we need to create `index.md` and `about.md` files, and populate them with some markdown.

As a shortcut, we can use Jasper Van der Jeugt's ['lorum-markdownum' website](https://github.com/jaspervdj/lorem-markdownum) site to generate pages of random Markdown text automatically:

    $ curl 'jaspervdj.be/lorem-markdownum/markdown.txt' > docs/index.md
    $ curl 'jaspervdj.be/lorem-markdownum/markdown.txt' > docs/about.md

When you're done the `docs` directory should look like this:

    $ ls docs
    about.md index.md

Okay, we're ready to build  our documentation now. MkDocs comes with a built-in webserver, that lets you preview your documentation as you work on it. We start the webserver by making sure we're in the same directory as the `mkdocs.yml` config file, and then running the `mkdocs serve` command:

    $ mkdocs serve
	Running at: http://127.0.0.1:8000/

Open up [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser, and you'll see the index page being displayed:

![Screenshot](img/screenshot.png)

The webserver also supports auto-reloading, and will rebuild your documentation whenever anything in the configuration file, documentation directory or theme directory changes.

Go ahead and edit the `doc/index.md` document, and change the initial heading to `MkDocs`, then reload the site in your browser, and you should see the change take effect immediately.

We can also change the configuration file to alter how the documentation is displayed.  Let's go ahead and change the theme.  Edit the `mkdocs.yaml` file to the following:

    site_name: 'MkLorum'
    pages:
    - ['index.md', 'Home']
    - ['about.md', 'About']
    theme: readthedocs

Refresh the browser again, and you'll now see the ReadTheDocs theme being used.

![Screenshot](img/readthedocs.png)

---

## Building & deploying

That's looking good.  We're ready to deploy the first pass of our `MkLorum` documentation now.  Let's build the documentation.

    $ mkdocs build

This will create a new directory, named `site`.  Let's take a look inside the directory:

    $ ls site
    about css fonts img index.html js

Notice that our source documentation has been output as two HTML files named `index.html` and `about/index.html`.  We also have various other media that's been copied into the `site` directory as part of the documentation theme.

If you're using source code control such as `git` you probably don't want to check your documentation builds into the repository.  Add the following to your `.gitignore` file:

    site/

If you don't have a `.gitignore` file in the current directory you should probably create one now.  If you're using another source code control you'll want to check it's documentation on how to ignore specific directories.

The documentation site that we've just built only uses static files so you'll be able to host it from pretty much anywhere. [GitHub project pages](https://help.github.com/articles/creating-project-pages-manually) and [Amazon S3](http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html) are good hosting options. Upload the contents of the entire `site` directory to wherever you're hosting your website from and you're done.
