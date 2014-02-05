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

As a shortcut, we can use the [`lorum-markdownum` API](https://github.com/jaspervdj/lorem-markdownum) to generate some markdown text automatically:

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

Mea dicta aliquid ornatus cu, duis sanctus disputationi his in. Rebum adolescens definiebas vis te. Ornatus noluisse mel te, modo utinam ea sit, putent omittantur quo ad. Ius ad dicta iusto, vel ne nonumy quaestio.

    $ mkdocs build

Quo ad delectus praesent quaerendum. Ridens deleniti iracundia est eu. Ex vis labitur adipisci laboramus, eu corrumpit maiestatis mea, in usu graeci apeirian moderatius. Id adhuc decore facilis pro, ad meliore dolorem sea. Iudico partiendo ex eum. Illud illum molestiae ea ius, mei iusto audire te.

