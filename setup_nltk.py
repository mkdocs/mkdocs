#!/usr/bin/env python

import os, sys
"""  Need to set NLTK_DATA """

os.environ['NLTK_DATA'] = os.path.expanduser("~") + '/nltk_data'
print "Trying to download data to: " + os.environ['NLTK_DATA']

if not os.path.exists(os.environ['NLTK_DATA']):
    try:
        os.makedirs(os.environ['NLTK_DATA'])
    except:
        print "Failed to create " + os.environ['NLTK_DATA']
        sys.exit(1)

import nltk
nltk.download("stopwords")
