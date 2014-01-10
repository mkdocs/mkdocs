#!/usr/bin/env python
#coding: utf-8

import collections
import jinja2
import markdown
import os
import re
import shutil
import yaml


config = yaml.load(open('mkdoc.yaml', 'r'))

# For preview builds only...
base_url = 'file://%s' % os.path.normpath(os.path.join(os.getcwd(), config['output_dir']))
suffix = '.html'
index = 'index.html'


def build_theme(config):
    for (source_dir, dirnames, filenames) in os.walk(config['theme_dir']):
        relative_path = os.path.relpath(source_dir, config['theme_dir'])
        output_dir = os.path.normpath(os.path.join(config['output_dir'], relative_path))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in filenames:
            if not filename.endswith('.html'):
                source_path = os.path.join(source_dir, filename)
                output_path = os.path.join(output_dir, filename)
                shutil.copy(source_path, output_path)


def build_statics(config):
    for (source_dir, dirnames, filenames) in os.walk(config['source_dir']):
        relative_path = os.path.relpath(source_dir, config['source_dir'])
        output_dir = os.path.normpath(os.path.join(config['output_dir'], relative_path))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in filenames:
            if not filename.endswith('.md'):
                source_path = os.path.join(source_dir, filename)
                output_path = os.path.join(output_dir, filename)
                shutil.copy(source_path, output_path)
                #print 'Static:', source_path, '->', output_path


def build_html(config):
    nav = build_nav(config)
    template_path = os.path.join(config['theme_dir'], 'base.html')
    template = jinja2.Template(open(template_path, 'r').read())

    for path, title in config['index']:
        homepage_url = path_to_url('index.md', config)
        url = path_to_url(path, config)
        previous_url, next_url = path_to_previous_and_next_urls(path, config)

        html_path = os.path.splitext(path)[0] + '.html'
        source_path = os.path.join(config['source_dir'], path)
        output_path = os.path.join(config['output_dir'], html_path)

        # Get the markdown text
        source_content = open(source_path, 'r').read().decode('utf-8')

        # Prepend a table of contents marker for the TOC extension
        source_content = '[TOC]\n\n<!-- ENDTOC -->' + source_content

        # Generate the HTML from the markdown source
        content = markdown.markdown(source_content, extensions=['toc'])

        # Strip out the generated table of contents
        (toc, content) = content.split('<!-- ENDTOC -->', 1)
        toc = '\n'.join(toc.splitlines()[2:-1])
        toc = '<ul class="nav bs-sidenav">\n' + toc

        # Replace links ending in .md with links to the generated HTML instead
        content = re.sub(r'a href="([^"]*)\.md"', r'a href="\1%s"' % suffix, content)
        content = re.sub('<pre>', '<pre class="prettyprint">', content)

        context = {
            'project_name': config['project_name'],
            'content': content,
            'toc': toc,
            'url': url,
            'base_url': base_url,
            'homepage_url': homepage_url,
            'previous_url': previous_url,
            'next_url': next_url,
            'nav': nav
        }
        output_content = template.render(context)

        open(output_path, 'w').write(output_content.encode('utf-8'))
        #print 'HTML:', source_path, '->', output_path


def build_nav(config):
    ret = collections.OrderedDict()
    for path, title in config['index']:
        url = path_to_url(path, config)
        title, sep, child = title.partition('/')
        title = title.strip()
        child = child.strip()
        if not child:
            ret[title] = url
        elif title not in ret:
            ret[title] = collections.OrderedDict({child: url})
        else:
            ret[title][child] = url
    return ret


def path_to_url(path, config):
    path = os.path.splitext(path)[0]
    url = path.replace(os.path.pathsep, '/')
    url = base_url + '/' + url
    if config['url_strip_index_files'] and (url == 'index' or url.endswith('/index')):
        return url.rstrip('index')
    elif not config['url_strip_html_suffix']:
        return url + '.html'
    return url


def path_to_previous_and_next_urls(current_path, config):
    paths = [path for path, title in config['index']]
    idx = paths.index(current_path)

    if idx == 0:
        prev = None
    else:
        prev = path_to_url(paths[idx - 1], config)

    if idx + 1 >= len(paths):
        next = None
    else:
        next = path_to_url(paths[idx + 1], config)

    return (prev, next)


build_theme(config)
build_statics(config)
build_html(config)
