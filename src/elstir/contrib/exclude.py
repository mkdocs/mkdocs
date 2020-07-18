import fnmatch
import re
import os
import sys
import elstir
import elstir.plugins
import elstir.structure.files

class Exclude(elstir.plugins.BasePlugin):
    """A elstir plugin that removes all matching files from the input list."""

    config_scheme = (
        ('glob', elstir.config.config_options.Type((str, list), default=None)),
        ('regex', elstir.config.config_options.Type((str, list), default=None)),
    )

    def on_files(self, files, config):
        globs = self.config['glob'] or []
        if not isinstance(globs, list):
            globs = [globs]
        regexes = self.config['regex'] or []
        if not isinstance(regexes, list):
            regexes = [regexes]
        out = []
        def include(name):
            for g in globs:
                if fnmatch.fnmatchcase(name, g):
                    return False
            for r in regexes:
                if re.match(r, name):
                    return False
            return True
        for i in files:
            name = i.src_path
            if not include(name):
                continue

            # Windows reports filenames as eg.  a\\b\\c instead of a/b/c.
            # To make the same globs/regexes match filenames on Windows and
            # other OSes, let's try matching against converted filenames.
            # On the other hand, Unix actually allows filenames to contain
            # literal \\ characters (although it is rare), so we won't
            # always convert them.  We only convert if os.sep reports
            # something unusual.  Conversely, some future elstir might
            # report Windows filenames using / separators regardless of
            # os.sep, so we *always* test with / above.
            if os.sep != '/':
                namefix = name.replace(os.sep, '/')
                if not include(namefix):
                    continue
            out.append(i)
        return elstir.structure.files.Files(out)