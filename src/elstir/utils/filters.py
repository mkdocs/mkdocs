from pathlib import Path
from functools import reduce
import json,os,sys
import jinja2

import yaml

from elstir.utils import normalize_url


class Resource: pass


def get_nest(data, *args):
    """https://stackoverflow.com/questions/10399614/accessing-value-inside-nested-dictionaries"""
    if args and data:
        element  = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nest(value, *args[1:])

def tojson(obj, **kwargs):
    return jinja2.Markup(json.dumps(obj, **kwargs))


@jinja2.contextfilter
def url_filter(context, value):
    """ A Template filter to normalize URLs. """
    return normalize_url(value, page=context['page'], base=context['base_url'])

def _get_gallery_filters(children_data):
    """
    Used in aurore tmpl-0001
    """
    filters = {}
    for child in children_data:
        for fltr in child["template_data"]:
            if fltr not in filters:
                filters.update({fltr: [child["template_data"][fltr]]})
            elif child["template_data"][fltr] not in filters[fltr]:
                filters[fltr].append(child["template_data"][fltr])
    return filters

def getParentTemplateFields(abs_src_path, data_fields,filtered=False):
    if data_fields: # and "template_data" in page.meta:
        data_files = data_fields['gallery_items']
        filters = data_fields["filters"] if "filters" in data_fields else []
        folder, _ = os.path.split(abs_src_path)
        child_data = {}
        for filename in data_files:
            try:
                with open(Path(folder)/filename) as f: data = yaml.load(f,Loader=yaml.Loader)
                for prop in data_files[filename]:
                    if isinstance(data_files[filename], dict):
                        key = data_files[filename][prop]

                    if not filtered or (prop in filters):
                        try:
                            child_data.update({key: get_nest(data, *key.split('.'))})
                        except Exception as e:
                            pass
                            # print(e,sys.exc_info())
            except Exception as e:
                pass
                # print("EXCEPTION",e,sys.exc_info())
        return child_data

@jinja2.contextfilter
def get_children(context,page,pages,depth=2):
    """"""
    folder, file = os.path.split(page.file.abs_src_path)
    list_of_files = []
    #num_pages_in_dir = len([pg for pg in os.listdir(folder) if os.path.isfile(os.path.join(folder,pg)) and pg[0]!='.' and pg[~2:]=='.md'])
    num_pages_in_dir = sum(1 for pg in Path(folder).glob("*.md") if pg.name[0]!='.')
    dirs = [dr for dr in Path(folder).glob("*/") if  "img" not in dr.name]
    num_sub_dirs = len(dirs)
    try:
        if num_pages_in_dir > 1 and num_sub_dirs <= 1:
            list_of_files = _index_files(folder,pages,page,depth)
            return list_of_files
        elif num_pages_in_dir == 1 or (file=='index.md' and num_sub_dirs >0):
            list_of_files = _index_dirs(folder,pages,page,depth)
            return list_of_files

        else: return {}
    except Exception as e:
        # print(f'EXCEPTION: get_children: {e}')
        return {}


def elstir_get_filters(template_data: dict)-> dict:
    if "filters" in template_data:
        gallery_items = template_data['gallery_items']
        filters = template_data['filters']
        # print(gallery_items,filters)
        args = [{k:v} for f in gallery_items.values() for k,v in f.items() if k in filters]
        return reduce(lambda x,y: {**x,**y},args)
    else:
        return {}



def _get_resource_meta(page: object, extra_data:dict=None):
    meta = page.meta
    try:
        extra_meta = getParentTemplateFields(page.file.abs_src_path,extra_data)
        meta = {
            **meta,
            **(extra_meta if extra_meta else {})
            }
    except Exception as e:
        print(f'Exception - _get_resource_meta: {e}')
    return meta



@jinja2.contextfilter
def sidebar(context,page,pages):
    depth = len(context['base_url'].split('/'))
    min_depth = context['config']['sidebar']['min_depth']
    max_depth = context['config']['sidebar']['max_depth']
    if depth <= min_depth or depth >= max_depth: return {}
    folder,file = os.path.split(page.file.abs_src_path)
    list_of_files = []
    #num_pages_in_dir = len([pg for pg in os.listdir(folder) if os.path.isfile(os.path.join(folder,pg)) and pg[0]!='.' and pg[~2:]=='.md'])
    #dirs = [dr for dr in os.listdir(folder) if not os.path.isfile(os.path.join(folder,dr))]
    num_pages_in_dir = sum(1 for pg in Path(folder).glob("*.md") if pg.name[0]!='.')
    dirs = [dr for dr in Path(folder).glob("*/") if  "img" not in dr.name]
    num_sub_dirs = len(dirs)
    try:
        if depth==min_depth+1 and num_pages_in_dir == 1 and num_sub_dirs > 0:
            list_of_files.append({
                 "title": page.title,
                 "active": True,
                 "url": page.abs_url,
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
        elif num_pages_in_dir == 1 or file=='index.md':
            list_of_files = _index_dirs(os.path.dirname(folder),pages,page)
            return list_of_files

        elif num_pages_in_dir > 1: #and num_sub_dirs<=1:
            list_of_files = _index_files(folder,pages,page)
            return list_of_files
        else: return {}
    except Exception as e:
        # print(e)
        return {}

def _get_dir_index(path,pages,folder=None):
    if folder is not None: path = os.path.join(folder,path)
    index = None
    for page in pages:
        if page.abs_src_path == os.path.join(path,'index.md'):
            index = page
    if not index:
        for page in pages:
            if page.abs_src_path == os.path.join(path,'README.md'):
                index = page
    return index

def _get_dir_image(page_path):
    folder = os.path.basename(os.path.dirname(page_path))
    path, _ = os.path.split(page_path)
    item_id = os.path.dirname(page_path)
    image_path = os.path.join(path,'main.png')

    if os.path.isfile(os.path.join(folder,folder + ".png")):
        return os.path.join( folder, folder+".png")
    elif os.path.isfile(image_path):
        return os.path.join( folder,'main.png' )
    elif os.path.isfile(os.path.join(path,'main.svg')):
        return os.path.join(folder,'main.svg')
    else:
        return False


def _index_dirs(folder, pages, page, depth=2):
    list_of_files = []
    dirs = [dr for dr in Path(folder).glob("*/") if  "img" not in dr.name]
    #dirs = [dr for dr in os.listdir(folder) if not os.path.isfile(os.path.join(folder,dr))]
    if _get_dir_index(folder,pages):
        list_of_files.append({
            "title": _get_dir_index(folder,pages).page.title,
            "active": page.file.abs_src_path == os.path.join(folder,'index.md'),
            "url": _get_dir_index(folder,pages).page.abs_url,
            "level": 1,
            "children": _get_dir_children(dirs, pages, folder, page, 2, depth),
            })
        if "template_data" in page.meta:
            list_of_files[0].update({"filters": _get_gallery_filters(
                list_of_files[0]["children"]
            )})
        return list_of_files
    else: return {}

def _get_dir_page(path,pages,folder=None):
    if folder is not None: path = os.path.join(folder,path)
    for page in pages:
        if page.abs_src_path == path:
            return page

def _index_files(folder, pages, page, depth=2):
    list_of_files = []
    files = [dr for dr in os.listdir(folder) if os.path.isfile(os.path.join(folder,dr))]
    list_of_files.append({
         "title": "{}".format( _get_dir_index(folder,pages).page.title),
         "active": page.file.abs_src_path == os.path.join(folder,'index.md'),
         "url": _get_dir_index(folder,pages).page.abs_url,
         "level": 1,
         "children": _get_idx_children(files, pages, folder, page, 2),
        })
    return list_of_files

def _get_dir_children(dirs, pages, folder, current_page: object, level, depth):
    children = []
    if "template_data" in current_page.meta:
        data_fields = current_page.meta['template_data']
        # print(current_page.meta)
        # print(f"_get_dir_children.data_fields : {data_fields}")
    else:
        data_fields = False
    # print("GET_DIR_CHILDREN")
    for dr in dirs:
        file = _get_dir_index(dr,pages,folder)
        if file:
            page = file.page
            if level <= depth:
                sub_folder = os.path.join(folder,dr)
                sub_dirs = [sdr for sdr in os.listdir(sub_folder) if not os.path.isfile(os.path.join(sub_folder,sdr))]
                sub_children = _get_dir_children(sub_dirs, pages, sub_folder, page, level+1, depth)
                if not sub_children:
                    files = [sdr for sdr in os.listdir(sub_folder) if os.path.isfile(os.path.join(sub_folder,sdr))]
                    sub_children = _get_idx_children(files, pages, sub_folder, page, level+1)
            else:
                sub_children = []
            children.append({
                "title": page.title,
                "active": page.file.abs_src_path == current_page.file.abs_src_path,
                "url": page.abs_url,
                "synopsis": _get_description(page),
                "level": level,
                "image": _get_dir_image(page.file.abs_src_path),
                "meta": _get_resource_meta(page,extra_data=data_fields), #page.meta, #
                "children":  sub_children,
                "template_data": getParentTemplateFields(page.file.abs_src_path, data_fields, filtered=True)
                })
    return children


def _get_idx_children(files, pages, folder, current_page, level):
    children = []
    # print("INDEXING CHILDREN: {}".format(folder))
    for file in files:
        file = _get_dir_page(file,pages,folder)
        
        if file and os.path.basename(file.src_path).lower() not in ['index.md', 'readme.md']:
            page = file.page
            # print("     {}".format(page.title))
            children.append({
                "title": "{}".format(page.title),
                "active": page.file.abs_src_path == current_page.file.abs_src_path,
                "url": page.abs_url,
                "synopsis": _get_description(page),
                "level": level,
                "as_code": True,
                "meta": page.meta,
                "children": [],
                # "template_data": getParentTemplateFields(page, page.meta)
                })
    return children

def _get_description(page):
    if "summary" in page.meta:
        return page.meta["summary"]
    if "abstract" in page.meta:
        return page.meta["abstract"]
    elif "description" in page.meta:
        return page.meta["description"]
    elif "synopsis" in page.meta:
        return page.meta["synopsis"]
    else:
        return False


