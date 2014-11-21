import inspect
import jinja2
import os
import re
import sys
import shutil

from webhelpers.html.tools import strip_tags
from mkdocs import nav, build
from . import config

MEMBER_KINDS = [
    'Module',
    'Class',
    'Variable',
    'Member',
    'Property',
    'Function',
    'Method',
    'Signal',
    'Slot',
    'Abstract Method',
    'Class Method',
    'Static Method',
    'Deprecated Method',
    'Builtin',
]

MEMBER_PRIVACY = [
    '',
    'Public',
    'Imported Public',
    'Protected',
    'Imported Protected',
    'Private',
    'Imported Private',
]

SECTIONS = [' '.join((privacy, kind)) for privacy in MEMBER_PRIVACY for kind in MEMBER_KINDS]
API_PAGES = {}

def _pre_process_objects(text):
    # replace references to objects
    for result in re.findall('\<(\w+)\>', text):
        if '.' in result:
            module_name, _, name = result.rpartition('.')
            try:
                module = sys.modules[module_name]
                obj = getattr(module, name)
                url = API_PAGES[obj].abs_url
                text = text.replace('<' + result + '>', '[{0}]({1})'.format(name, url))
            except (KeyError, AttributeError):
                text = text.replace('<' + result + '>', '`{0}`'.format(name))
        else:
            py_obj = None
            for obj in API_PAGES:
                if obj.__name__ == result:
                    py_obj = obj
                    break

            try:
                url = API_PAGES[py_obj].abs_url
                text = text.replace('<' + result + '>', '[{0}]({1})'.format(result, url))
            except (KeyError, AttributeError):
                text = text.replace('<' + result + '>', '`{0}`'.format(result))

    return text

#--------------------------------

class Member(object):
    def __init__(self, data, functionType='Method'):
        if type(data) == tuple:
            name = data[0]
            kind = data[1]
            cls = data[2]
            obj = data[3]
        else:
            name = data.name
            kind = data.kind
            cls = data.defining_class
            obj = data.object

        try:
            kind = data.object.func_type
        except AttributeError:
            pass

        qtype_docs = ''

        # strip out private member headers
        results = re.match('^(_\w+)(__.+)', name)
        if results:
            name = results.group(2)

        # determine the privacy level
        if name.startswith('__'):
            privacy = 'Private'
        elif name.startswith('_'):
            privacy = 'Protected'
        else:
            privacy = 'Public'

        # look for specific kind information
        if inspect.ismodule(obj):
            kind = 'Module'

        elif inspect.isclass(obj):
            kind = 'Class'

        elif kind == 'method':
            type_name = type(obj).__name__

            if type_name in ('pyqtSignal', 'Signal'):
                kind = 'Signal'
                qtype_docs = str(obj)

            elif type_name in ('pyqtSlot', 'Slot'):
                kind = 'Slot'
                qtype_docs = str(obj)

            elif type_name in ('pyqtProperty', 'Property'):
                kind = 'Property'
            elif name.startswith('__') and name.endswith('__'):
                kind = 'Builtin'
            else:
                kind = 'Method'

        elif isinstance(obj, staticmethod):
            kind = 'Static Method'
            obj = getattr(cls, name, None)

        elif isinstance(obj, classmethod):
            kind = 'Class Method'
            obj = getattr(cls, name, None)

        elif inspect.ismethod(obj) or inspect.ismethoddescriptor(obj):
            if name.startswith('__') and name.endswith('__'):
                kind = 'Builtin'
            else:
                kind = 'Method'

        elif inspect.isbuiltin(obj):
            kind = 'Variable'

        elif inspect.isfunction(obj) or callable(obj):
            if name.startswith('__') and name.endswith('__'):
                kind = 'Builtin'
            else:
                kind = functionType

        else:
            kind = 'Variable'

        # setup the property information
        self.name = name
        self.defining_class = cls
        self.object = obj
        self.kind = kind
        self.is_callable = callable(obj) and not inspect.isclass(obj)
        self.privacy = privacy
        self.qtype_docs = qtype_docs

    @property
    def args(self):
        obj = self.object
        try:
            opts = (obj, obj.im_func)
        except AttributeError:
            opts = (obj,)

        out = ''
        for opt in opts:
            try:
                out = inspect.formatargspec(*inspect.getargspec(self.object))
            except TypeError:
                continue

        if not out:
            try:
                out = self.object.func_args
            except AttributeError:
                out = '(...) [unknown]'

        # ignore default properties for class methods & instance methods
        if self.kind == 'Class Method':
            out = out.replace('(cls, ', '(')
            out = out.replace('(cls)', '()')

        elif self.kind == 'Method':
            out = out.replace('(self, ', '(')
            out = out.replace('(self)', '()')

        return out

    @property
    def raw_docs(self):
        try:
            return inspect.getdoc(self.object)
        except AttributeError:
            try:
                return inspect.getcomments(self.object)
            except AttributeError:
                return getattr(self.object, '__doc__', '')

    @property
    def reimpliments(self):
        return ''

    @property
    def reimplimented(self):
        return ''

    @property
    def html_docs(self):
        text = self.raw_docs
        if not text:
            return ''

        text = _pre_process_objects(text)
        return build.convert_markdown(text, extensions=config.base_config['markdown_extensions'])[0]

    @property
    def url(self):
        try:
            return API_PAGES[self.object].abs_url
        except KeyError:
            return ''

    @property
    def source_filepath(self):
        try:
            page = API_PAGES[self.object]
            return page.source_filepath
        except (KeyError, AttributeError):
            return ''

    @property
    def url_class(self):
        return 'text-danger' if not self.url else ''

    @property
    def section(self):
        return ' '.join((self.privacy, self.kind)).strip()

#--------------------------------

class ApiPage(nav.Page):
    def __init__(self, **kwds):
        # pop off the ApiPage requirements
        py_object = kwds.pop('py_object', None)
        base_path = kwds.pop('base_path', '')

        # initialize the base page
        super(ApiPage, self).__init__(**kwds)

        # setup the pathing options
        if inspect.ismodule(py_object):
            path = py_object.__name__.replace('.', '/') + '/index.html'

        elif inspect.isclass(py_object):
            module = sys.modules[py_object.__module__]
            path = module.__name__.replace('.', '/') + '/{0}/index.html'.format(py_object.__name__)

        # store the custom attributes
        self._members = None
        self._all_members = None
        self.base_path = base_path
        self.py_object = py_object
        if base_path:
            self.output_path = base_path.rstrip('/') + '/' + path
        else:
            self.output_path = path

        # cache this object as a page
        API_PAGES[py_object] = self

    @property
    def all_members(self):
        return []

    @property
    def brief(self):
        text = strip_tags(self.html_docs)
        if len(text) > 200:
            return text[:200] + '...'
        else:
            return ''

    def collect_pages(self):
        pass

    def collect_members(self):
        return []

    def export_markdown(self, outpath):
        basepath = os.path.abspath(os.path.normpath(outpath))

        # clear the existing markdown
        if os.path.exists(outpath):
            shutil.rmtree(outpath)

        os.mkdir(basepath)
        for page in [self] + self.collect_pages():
            filepath = os.path.join(basepath, page.source_path)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            filename = os.path.join(filepath, page.source_file)
            content = page.generate_markdown()
            with open(filename, 'w') as f:
                f.write(content)

    def generate_markdown(self):
        theme_path = os.path.join(os.path.dirname(__file__), 'themes', 'markdown')
        loader = jinja2.FileSystemLoader(theme_path)
        env = jinja2.Environment(loader=loader)

        template = env.get_template(self.template_name.replace('.html', '.md'))
        return template.render(self.render_context)

    @property
    def members(self):
        if self._members is None:
            self._members = self.collect_members()
        return self._members

    @property
    def html_docs(self):
        text = self.raw_docs
        if not text:
            return ''

        text = _pre_process_objects(text)
        return build.convert_markdown(text, extensions=config.base_config['markdown_extensions'])[0]

    @property
    def object_name(self):
        return self.py_object.__name__

    @property
    def render_context(self):
        context = {
            'page': self,
            'object_name': self.object_name,
            'title': self.object_title,
            'members': self.members,
            'brief': self.brief,
            'details': self.html_docs,
            'sections': self.sections,
        }
        return context

    @property
    def object_title(self):
        return getattr(self.py_object, '__title__', self.py_object.__name__)

    @property
    def inherits(self):
        return []

    @property
    def inherited_by(self):
        return []

    @property
    def raw_docs(self):
        try:
            return inspect.getdoc(self.py_object)
        except AttributeError:
            try:
                return inspect.getcomments(self.py_object)
            except AttributeError:
                return getattr(self.py_object, '__doc__', '')

    @property
    def sections(self):
        output = {}
        for member in self.members:
            output.setdefault(member.section, [])
            output[member.section].append((member, type(member.object).__name__))

        items = output.items()
        items.sort(key=lambda x: SECTIONS.index(x[0]))
        return items

    @property
    def source_path(self):
        return ''

    @property
    def source_file(self):
        return 'index.md'

    @property
    def source_filepath(self):
        return os.path.join(self.base_path, self.source_path, self.source_file).replace('\\', '/')

    @property
    def template_name(self):
        if inspect.ismodule(self.py_object):
            return 'module.html'
        else:
            return 'class.html'

    @property
    def url(self):
        return '/' + self.abs_url

#----------------------------------------

class ModulePage(ApiPage):
    def collect_members(self):
        """
        Collects all the members for this dox object and caches them.
        """
        # load all the items
        try:
            members = dict(inspect.getmembers(self.py_object))
        except AttributeError:
            members = {}

        for key in dir(self.py_object):
            if not key in members:
                try:
                    members[key] = getattr(self.py_object, key, None)
                except AttributeError:
                    continue

        output = []
        for name, obj in sorted(members.items()):
            if inspect.isclass(self.py_object):
                func_type = 'Static Method'
            else:
                m_name = self.py_object.__name__
                try:
                    o_name = inspect.getmodule(obj).__name__
                except AttributeError:
                    continue

                if m_name not in o_name:
                    continue

                func_type = 'Function'

            output.append(Member((name, kind, None, obj), func_type))
        return output

    def collect_pages(self):
        pages = []
        previous = self
        for member in self.members:
            if member.object in API_PAGES:
                continue

            if inspect.ismodule(member.object):
                name = member.object.__name__.split('.')[-1]
                url = self.base_path.rstrip('/') + '/' + member.object.__name__.replace('.', '/')
                page = ModulePage(py_object=member.object,
                                  base_path=self.base_path,
                                  title=name,
                                  url=url,
                                  path=member.object.__file__,
                                  url_context=self.url_context)

                page.previous_page = previous
                previous.next_page = page
                previous = page

                # collect the module
                pages.append(page)

                # # collect the sub-modules (and update the linked list in the process)
                sub_pages = page.collect_pages()
                if sub_pages:
                    page.next_page = sub_pages[0]
                    sub_pages[0].previous_page = page
                    previous = sub_pages[-1]
                    pages += sub_pages

            elif inspect.isclass(member.object) and member.object.__module__ == self.py_object.__name__:
                module_name = member.object.__module__
                module = sys.modules[module_name]
                name = member.object.__name__
                url = self.base_path.rstrip('/') + '/' + module_name.replace('.', '/') + '/' + name

                page = ClassPage(py_object=member.object,
                                 base_path=self.base_path,
                                 title=name,
                                 url=url,
                                 path=module.__file__,
                                 url_context=self.url_context)

                page.previous_page = previous
                previous.next_page = page
                previous = page
                pages.append(page)

        return pages

    @property
    def render_context(self):
        context = super(ModulePage, self).render_context
        modsplit = self.py_object.__name__.split('.')
        breadcrumbs = []
        for i in xrange(len(modsplit) - 1):
            try:
                module = sys.modules['.'.join(modsplit[:i+1])]
                path = '<a href="{0}">{1}</a>'.format(API_PAGES[module].abs_url, modsplit[i])
                breadcrumbs.append(path)
            except KeyError:
                breadcrumbs.append('<a name="{0}" class="text-danger">{0}"</a>'.format(modsplit[i]))

        breadcrumbs.append(modsplit[-1])

        context['breadcrumbs'] = breadcrumbs
        return context

    @property
    def source_path(self):
        if '__init__' in self.py_object.__file__:
            return os.path.join(*self.py_object.__name__.split('.'))
        else:
            return os.path.join(*self.py_object.__name__.split('.')[:-1])

    @property
    def source_file(self):
        if '__init__' in self.py_object.__file__:
            return 'index.md'
        else:
            return self.py_object.__name__.split('.')[-1] + '.md'

#----------------------------------------

class ClassPage(ApiPage):
    @property
    def all_members(self):
        if self._all_members is None:
            self._members = self.collect_members()
        return self._all_members

    @property
    def render_context(self):
        context = super(ClassPage, self).render_context

        # create the breadcrumbs
        modsplit = self.py_object.__module__.split('.')
        breadcrumbs = []
        for i in xrange(len(modsplit)):
            try:
                module = sys.modules['.'.join(modsplit[:i+1])]
                link = '<a href="{0}">{1}</a>'.format(API_PAGES[module].abs_url, modsplit[i])
            except KeyError:
                link = '<a name="{0}" class="text-danger">{0}</a>'.format(modsplit[i])
            breadcrumbs.append(link)
        context['breadcrumbs'] = breadcrumbs

        # create the inheritance information
        inherits = []
        for obj in self.inherits:
            # ignore base class type
            if obj == object:
                continue

            try:
                link = '<a href="{0}">{1}</a>'.format(API_PAGES[obj].abs_url, obj.__name__)
            except KeyError:
                link = '<a name="{0}" class="text-danger">{0}</a>'.format(obj.__name__)
            inherits.append(link)
        context['inherits'] = inherits

        # create the inheritance information
        inherited_by = []
        for obj in self.inherited_by:
            try:
                link = '<a href="{0}">{1}</a>'.format(API_PAGES[obj].abs_url, obj.__name__)
            except KeyError:
                link = '<a name="{0}" class="text-danger">{0}</a>'.format(obj.__name__)
            inherited_by.append(link)
        context['inherited_by'] = inherited_by

        return context

    def collect_members(self):
        try:
            members = inspect.classify_class_attrs(self.py_object)
        except AttributeError:
            members = []

        self._all_members = [Member(x) for x in members]
        return [x for x in self._all_members if x.defining_class == self.py_object]

    @property
    def inherits(self):
        return self.py_object.__bases__

    @property
    def inherited_by(self):
        return [obj for obj in API_PAGES if inspect.isclass(obj) and self.py_object in obj.__bases__]

    @property
    def source_path(self):
        return os.path.join(*(self.py_object.__module__.split('.') + [self.py_object.__name__]))

def load_module(module_name, base_path, title='', url_context=None):
    __import__(module_name)
    module = sys.modules[module_name]
    title = title or module_name
    url = base_path.rstrip('/') + '/' + module.__name__.replace('.', '/')
    return ModulePage(py_object=module,
                      base_path=base_path,
                      title=title,
                      path=module.__file__,
                      url=url,
                      url_context=url_context)