import os

config_text = 'site_name: My Docs'
index_text = '# Welcome to MkDocs\n\nNow get writing those docs!'

def new(args, options):
    if len(args) != 1:
        print "Usage 'mkdocs new [directory-name]'"
        return

    output_dir = args[0]
    docs_dir = os.path.join(output_dir, 'docs')

    if not os.path.exists(output_dir):
        print 'Creating project directory: %s' % output_dir
        os.mkdir(output_dir)

    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)

    config_path = os.path.join(output_dir, 'mkdocs.yml')
    index_path = os.path.join(docs_dir, 'index.html')
    print 'Writing config file: %s' % config_path
    open(config_path, 'w').write(config_text)
    print 'Writing initial docs: %s' % index_path
    open(index_path, 'w').write(index_text)
