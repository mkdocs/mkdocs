from collections import defaultdict

callbacks = defaultdict(list)

def register_callback(event_type, callback):
    callbacks[event_type].append(callback)

#--------------------------------------------------------

class Event(object):
    def __init__(self):
        self.consumed = False

    """ Abstract event extension class for mkdocs """
    def broadcast(self):
        for callback in callbacks[type(self)]:
            callback(self)
            if self.consumed:
                return


# B
#--------------------------------------------------------

class BuildPage(Event):
    """ Called before a page is generated within the navigation system """
    def __init__(self, page_title, path, url, url_context):
        super(BuildPage, self).__init__()

        # input arguments
        self.page_title = page_title
        self.path = path
        self.url = url
        self.url_context = url_context

        # output arguments
        self.pages = []

# C
#--------------------------------------------------------

class CLI(Event):
    # define additional plugin commands
    commands = set()

    def __init__(self, config, cmd, args, options=None):
        super(CLI, self).__init__()

        # define the execution event
        self.config = config
        self.cmd = cmd
        self.args = args
        self.options = options

# G
#--------------------------------------------------------

class GenerateContent(Event):
    def __init__(self, config, page):
        super(GenerateContent, self).__init__()

        # inpute arguments
        self.config = config
        self.page = page

        # output arguments
        self.table_of_contents = ''
        self.meta = {}
        self.html_content = ''

# P
#--------------------------------------------------------

class PreBuild(Event):
    """ Called before a build event occurs """
    def __init__(self, config):
        super(PreBuild, self).__init__()

        self.config = config

