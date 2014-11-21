from collections import defaultdict

callbacks = defaultdict(list)

def register_callback(event_type, callback):
    """
    Registers a callback method to the given event type.

    :param      event_type | subclass of <Event>
                callback   | <callable>
    """
    callbacks[event_type].append(callback)

#--------------------------------------------------------

class Event(object):
    """ Abstract event extension class for mkdocs """
    def broadcast(self):
        """
        Broadcasts this event to all the listening callbacks.  If any callback consumes this event, then
        it will stop processing for all other events and return that it has already been processed.

        :return     <bool> | consumed
        """
        for callback in callbacks[type(self)]:
            if callback(self):
                return True
        return False

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

# E
#--------------------------------------------------------

class Execute(Event):
    # define additional plugin commands
    commands = set()

    def __init__(self, config, cmd, args, options=None):
        super(Execute, self).__init__()

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

