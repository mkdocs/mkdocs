"""
Copyright (c) 2015, Waylan Limberg
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may
be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

MultiMarkdown Meta-Data

Extracts, parses and transforms MultiMarkdown style data from documents.

"""


import re


#####################################################################
# Transformer Collection                                            #
#####################################################################

class TransformerCollection(object):
    """
    A collecton of transformers.

    A transformer is a callable that accepts a single argument (the value to be transformed)
    and returns a transformed value.
    """

    def __init__(self, items=None, default=None):
        """
        Create a transformer collection.

        `items`: A dictionary which points to a transformer for each key (optional).

        `default`: The default transformer (optional). If no default is provided,
        then the values of unknown keys are returned unaltered.
        """

        self._registery = items or {}
        self.default = default or (lambda v: v)

    def register(self, key=None):
        """
        Decorator which registers a transformer for the given key.

        If no key is provided, a "default" transformer is registered.
        """

        def wrap(fn):
            if key:
                self._registery[key] = fn
            else:
                self.default = fn
            return fn
        return wrap

    def transform(self, key, value):
        """
        Calls the transformer for the given key and returns the transformed value.
        """

        if key in self._registery:
            return self._registery[key](value)
        return self.default(value)

    def transform_dict(self, data):
        """
        Calls the transformer for each item in a dictionary and returns a new dictionary.
        """

        newdata = {}
        for k, v in data.items():
            newdata[k] = self.transform(k, v)
        return newdata


# The global default transformer collection.
tc = TransformerCollection()


def transformer(key=None):
    """
    Decorator which registers a transformer for the given key.

    If no key is provided, a "default" transformer is registered.
    """

    def wrap(fn):
        tc.register(key)(fn)
        return fn
    return wrap


#####################################################################
# Data Parser                                                       #
#####################################################################


BEGIN_RE = re.compile(r'^-{3}(\s.*)?')
META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
META_MORE_RE = re.compile(r'^([ ]{4}|\t)(\s*)(?P<value>.*)')
END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')


def get_raw_data(doc):
    """
    Extract raw meta-data from a text document.

    Returns a tuple of document and a data dict.
    """

    lines = doc.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    if lines and BEGIN_RE.match(lines[0]):
        lines.pop(0)

    data = {}
    key = None
    while lines:
        line = lines.pop(0)

        if line.strip() == '' or END_RE.match(line):
            break  # blank line or end deliminator - done
        m1 = META_RE.match(line)
        if m1:
            key = m1.group('key').lower().strip()
            value = m1.group('value').strip()
            try:
                data[key].append(value)
            except KeyError:
                data[key] = [value]
        else:
            m2 = META_MORE_RE.match(line)
            if m2 and key:
                # Add another line to existing key
                data[key].append(m2.group('value').strip())
            else:
                lines.insert(0, line)
                break  # no meta data - done
    return '\n'.join(lines).lstrip('\n'), data


def get_data(doc, transformers=tc):
    """
    Extract meta-data from a text document.

    `transformers`: A TransformerCollection used to transform data values.

    Returns a tuple of document and a (transformed) data dict.
    """

    doc, rawdata = get_raw_data(doc)
    return doc, transformers.transform_dict(rawdata)
