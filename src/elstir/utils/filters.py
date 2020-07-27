import json,os
import jinja2

from elstir.utils import normalize_url


def tojson(obj, **kwargs):
    return jinja2.Markup(json.dumps(obj, **kwargs))


@jinja2.contextfilter
def url_filter(context, value):
    """ A Template filter to normalize URLs. """
    return normalize_url(value, page=context['page'], base=context['base_url'])


@jinja2.contextfilter
def sidebar(context,page,pages):
    """"""
    depth = len(context['base_url'].split('/'))
    print("DEPTH: {}".format(depth))
    print(page.title)
    if depth <= 1: return {}
    page_paths = [pg.abs_src_path for pg in context['pages']]
    folder,file = os.path.split(page.file.abs_src_path)
    #folder = os.path.dirname(folder)
    list_of_files = []
    num_pages_in_dir = len([pg for pg in os.listdir(folder) if os.path.isfile(os.path.join(folder,pg))])
    dirs = [dr for dr in os.listdir(folder) if not os.path.isfile(os.path.join(folder,dr))]
    print(dirs)
    num_sub_dirs = len(dirs)
    if depth==2 and num_pages_in_dir == 1 and num_sub_dirs > 0:
        print(folder,file)
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(os.listdir(folder))
        #try:
        list_of_files.append({
             "title": page.title,
             "active": True,
             "url": page.url,
             "level": 1,
             "children": [{
                "title": _get_dir_index(dr,pages,folder).page.title,
                "active": False,
                "url": dr,
                "level": 2,
                "children": {}
                } for dr in dirs if _get_dir_index(dr,pages,folder)]
             })
        return list_of_files
        #except:
        #print('FAILED')
        #    return {} 
    elif num_pages_in_dir == 1 or file=='index.md':
        #print('elif---------------------------------------')
        list_of_files = _index_dirs(os.path.dirname(folder),pages,page)
        return list_of_files

    elif num_pages_in_dir > 1 and num_sub_dirs==0:
        #print('elif---------------------------------------')
        list_of_files = _index_files(folder,pages,page)
        return list_of_files
    else: return {}

def _get_dir_index(path,pages,folder=None):
    if folder is not None: path = os.path.join(folder,path)
#print('PATH: {}'.format(path))
    for page in pages:
#print(page.abs_src_path)
#print(os.path.join(path,'index.md'))
        if page.abs_src_path == os.path.join(path,'index.md'):
            return page

def _index_dirs(folder, pages, page):
    print("PATH: {}".format(folder))
    list_of_files = []
    dirs = [dr for dr in os.listdir(folder) if not os.path.isfile(os.path.join(folder,dr))]
#page =_get_dir_index(folder)
    if _get_dir_index(folder,pages):
        list_of_files.append({
            "title": _get_dir_index(folder,pages).page.title,
            "active": page.file.abs_src_path == os.path.join(folder,'index.md'),
            "url": _get_dir_index(folder,pages).page.abs_url,
            "level": 1,
            "children": [{
                "title": _get_dir_index(dr,pages,folder).page.title,
                "active": _get_dir_index(dr,pages,folder).page.file.abs_src_path == page.file.abs_src_path,
                "url": os.path.join('..',dr),
                "level": 2,
                "children": {}
                } for dr in dirs if _get_dir_index(dr,pages,folder)]
            })
    #print(list_of_files)
        return list_of_files
    else: return {}

def _get_dir_page(path,pages,folder=None):
    if folder is not None: path = os.path.join(folder,path)
#print('PATH: {}'.format(path))
    for page in pages:
#print(page.abs_src_path)
#print(os.path.join(path,'index.md'))
        if page.abs_src_path == path:
            return page

def _index_files(folder, pages, page):
    print('FILE: {}'.format(page.title))
    list_of_files = []
    files = [dr for dr in os.listdir(folder) if os.path.isfile(os.path.join(folder,dr))]
    #page =_get_dir_index(folder)
    list_of_files.append({
         "title": "{}".format( _get_dir_index(folder,pages).page.title),
         "active": page.file.abs_src_path == os.path.join(folder,'index.md'),
         "url": _get_dir_index(folder,pages).page.abs_url,
         "level": 1,
         "children": [{
            "title": "{}".format(_get_dir_page(file,pages,folder).page.title),
            "active": _get_dir_page(file,pages,folder).page.file.abs_src_path == page.file.abs_src_path,
            "url": _get_dir_page(file,pages,folder).page.abs_url,
            #"url": os.path.join(folder,os.path.splitext(file)[0]),
            "level": 2,
            "as_code": True,
            "children": {}
            } for file in files if _get_dir_page(file,pages,folder)]
         })
    #print(list_of_files)
    return list_of_files


