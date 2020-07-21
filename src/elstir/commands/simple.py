
import os, shutil

import jinja2

def simple(project_dir):

    config = dict(
        docs_dir=project_dir
    )

    # create '_temp_build/'
    os.mkdir('_temp_build/')

    # get site_name
    filename = os.path.join(project_dir, 'README.md') 
    with open(filename) as f: 
        firstline = f.readline().strip()
        site_name = firstline.replace('#','')

    config['site_name'] = site_name

    # create 'dir/elstir.yml'
    templates_dir = os.path.join('..','templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
    tm = env.get_template('simple.jinja')
    page = tm.render(config=config)
    with open('elsltir.yml','w+') as f: f.write(page)
    
