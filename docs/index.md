# MkDocs

Project documentation with Markdown.

---

## Overview

MkDocs is a **fast**, **simple** and **downright gorgeous** static site generator that's geared towards building project documentation.  Documentation source files are written in Markdown, and configured with a single yaml configuration file.

#### Host anywhere.

Builds completely static HTML sites that you can host on GitHub pages, Amazon S3, or anywhere else you choose.

#### Great built-in themes.

There's a stack of good looking themes included by default.  Choose from bootstrap, readthedocs, ghostwriter, or any of the 12 bootswatch themes.

#### Preview your documentation as you work on it.

The built-in devserver allows you to preview your documentation as your writing it.  It will even auto-reload whenever you save any changes, so all you need to do to see your latest edits is refresh your browser.

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

In order to run, mkdocs requires a single configuration file named `mkdocs.yaml` to exist in the current directory.

An sed aeque munere facilisi, modus tractatos quo ei. Eu veniam tincidunt cum.

    site_name: 'Cat indexer'
    pages:
    - ['index.md', 'Home']
    - ['about.md', 'About']

You documentation source files should all exist in a single directory.  By default this directory should be named `docs`.

Quo ex ceteros theophrastus, mel eius repudiandae an, has autem legendos ut. Eu quo moderatius interpretaris, pro ad homero tractatos cotidieque. His errem dictas instructior ad, tation causae ceteros ex eum. Nam falli dicunt te, mea et unum contentiones, ius noluisse rationibus cotidieque ei.

    $ ls docs
    about.md index.md

Quo ex ceteros theophrastus, mel eius repudiandae an, has autem legendos ut. Eu quo moderatius interpretaris, pro ad homero tractatos cotidieque. His errem dictas instructior ad, tation causae ceteros ex eum. Nam falli dicunt te, mea et unum contentiones, ius noluisse rationibus cotidieque ei.

    $ mkdocs serve

Mea dicta aliquid ornatus cu, duis sanctus disputationi his in. Rebum adolescens definiebas vis te. Ornatus noluisse mel te, modo utinam ea sit, putent omittantur quo ad. Ius ad dicta iusto, vel ne nonumy quaestio.

    $ mkdocs build

Quo ad delectus praesent quaerendum. Ridens deleniti iracundia est eu. Ex vis labitur adipisci laboramus, eu corrumpit maiestatis mea, in usu graeci apeirian moderatius. Id adhuc decore facilis pro, ad meliore dolorem sea. Iudico partiendo ex eum. Illud illum molestiae ea ius, mei iusto audire te.

