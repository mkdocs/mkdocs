# Writing your docs

How to write and layout your markdown source files.

---

## File layout

Your documentation source should be written as regular Markdown files, and placed in a directory somewhere in your project.  Normally this directory will be named `docs` and will exist at the top level of your project, alongside the `mkdocs.yml` configuration file.

The simplest project you can create will look something like this:

    mkdocs.yml
    docs/
        index.md

By convention your project homepage should always be named `index`.  Any of the following extensions may be used for your Markdown source files: `markdown`, `mdown`, `mkdn`, `mkd`, `md`.

You can also create multi-page documentation, by creating several markdown files:

    mkdocs.yml
    docs/
        index.md
        about.md
        license.md

The file layout you use determines the URLs that are used for the generated pages.
Given the above layout, pages would be generated for the following URLs:

    /
    /about/
    /license/

You can also include your Markdown files in nested directories if that better suits your documentation layout.

    docs/
        index.md
        user-guide/getting-started.md
        user-guide/configuration-options.md
        license.md

Source files inside nested directories will cause pages to be generated with nested URLs, like so:

    /
    /user-guide/getting-started/
    /user-guide/configuration-options/
    /license/


## Linking documents

MkDocs allows you to interlink your documentation by using regular Markdown hyperlinks.

#### Internal hyperlinks

When linking between pages in the documentation you can simply use the regular Markdown hyperlinking syntax, including the relative path to the Markdown document you wish to link to.

    Please see the [project license](license.md) for further details.

When the MkDocs build runs, these hyperlinks will automatically be transformed into a hyperlink to the appropriate HTML page.

When working on your documentation you should be able to open the linked Markdown document in a new editor window simply by clicking on the link.

If the target documentation file is in another directory you'll need to make sure to include any relative directory path in the hyperlink.

    Please see the [project license](../about/license.md) for further details.

You can also link to a section within a target documentation page by using an anchor link.  The generated HTML will correctly transform the path portion of the hyperlink, and leave the anchor portion intact.

    Please see the [project license](about.md#license) for further details.

<!--
#### Cross-referencing your documentation

Ex eam quem facilisi deserunt. Veri audiam audire id his, quo at aperiri moderatius. In admodum partiendo est, ei rebum minimum eam, singulis accusata delicatissimi eos ut. Imperdiet vulputate assueverit eos an, elit recusabo et usu. Eam ad euismod accusata vituperata. Oratio vocent nominavi ei eum.

    At mel verear persius torquatos, his dolores [Sensibus](ref:) id, alia urbanitas in usu.

Eam ad euismod accusata vituperata. Oratio vocent nominavi ei eum.

    Ne his mucius oporteat, [mea ut eros delicatissimi](ref:delicatissimi), iudico nonumes moderatius an mel.
-->

## Images and media

As well as the Markdown source files, you can also include other file types in your documentation, which will be copied across when generating your documentation site.  These might include images and other media.

For example, if you project documentation needed to include a [GitHub pages CNAME file](https://help.github.com/articles/setting-up-a-custom-domain-with-pages#setting-the-domain-in-your-repo) and a PNG formatted screenshot image then your file layout might look as follows:

    mkdocs.yml
    docs/
        CNAME
        index.md
        about.md
        license.md
        img/
            screenshot.png

To include images in your documentation source files, simply use any of the regular Markdown image syntaxes:

    Cupcake indexer is a snazzy new project for indexing small cakes.

    ![Screenshot](img/screenshot.png)

    *Above: Cupcake indexer in progress*

You image will now be embedded when you build the documentation, and should also be previewed if you're working on the documentation with a Markdown editor.

## Markdown extensions

MkDocs supports the following Markdown extensions.

<!--
#### Page metadata

Unum errem propriae vis cu, et deseruisse interpretaris eam. Illum graecis per an, ludus laoreet repudiare nec an, molestie recteque et eam. Purto duis rationibus id eum, pro et amet appetere referrentur, minim impedit ad ius. Et nostrud perfecto sapientem vix, et dicit impedit consequat vim. Vis liber blandit no.

At mel verear persius torquatos, his dolores sensibus id, alia urbanitas in usu. Te pri cibo blandit. Debet dolore periculis ei pro, eu vis vidit ignota, vim natum dicta cu. Et appareat delicata vix, mei at solum lorem quodsi, verterem electram sit eu. Eius malis cum an, pro malorum euripidis ad, oblique appetere est cu. Eos ei fugit deterruisset. Vix ei aliquip dolorem, usu te euripidis reformidans, volumus pertinacia ea eam.

    page_title: Lorum
	page_description: "lorum ipsum dolor"
	source_files: example.js, lorum.js

	# Lorum Ipsum

	Unum errem propriae vis cu, et deseruisse interpretaris eam. Illum graecis per an, ludus laoreet repudiare nec an, molestie recteque et eam.
-->

#### Tables

A simple table looks like this:

    First Header | Second Header | Third Header
    ------------ | ------------- | ------------
    Content Cell | Content Cell  | Content Cell
    Content Cell | Content Cell  | Content Cell

If you wish, you can add a leading and tailing pipe to each line of the table:

    | First Header | Second Header | Third Header |
    | ------------ | ------------- | ------------ |
    | Content Cell | Content Cell  | Content Cell |
    | Content Cell | Content Cell  | Content Cell |

Specify alignment for each column by adding colons to separator lines:

    First Header | Second Header | Third Header
    :----------- | :-----------: | -----------:
    Left         | Center        | Right
    Left         | Center        | Right

#### Fenced code blocks

Start with a line containing 3 or more backtick \` characters, and ends with the first line with the same number of backticks \`:

    ```
    Fenced code blocks are like Stardard
    Markdown’s regular code blocks, except that
    they’re not indented and instead rely on a
    start and end fence lines to delimit the code
    block.
    ```

<!--
#### Admonitions

Ad est nibh suscipiantur. Quaeque deleniti delectus an has, tempor accusamus eu vix. Et democritum expetendis nam, putent fuisset duo ea, elaboraret efficiendi no vis.

    !!! danger "Don't try this at home"
        May cause grevious bodily harm
-->
