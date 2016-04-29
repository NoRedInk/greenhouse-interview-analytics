# -*- coding: utf-8 -*-
import itertools
import string
import re

from stop_words import get_stop_words


TAG_DELIM_RE = re.compile(r'([.,;()]? +|\.$)')
COMPOUND_TAG_DELIM_RE = re.compile(r'([-_])')
PUNCT_ERASER = dict.fromkeys(map(ord, string.punctuation + ' '))


def split_tags(tags):
    if not tags:
        return []
    stop_words = get_stop_words('en')
    for tag in TAG_DELIM_RE.split(tags):
        if tag in stop_words:
            continue
        cleaned = clean_tag(tag)
        if cleaned:
            yield cleaned.lower()


def clean_tag(tag):
    '''
    >>> clean_tag('(solar-eclipse)')
    'solar-eclipse'
    '''
    if not tag.translate(PUNCT_ERASER):
        return
    parts = COMPOUND_TAG_DELIM_RE.split(tag.strip())
    words = [part.translate(PUNCT_ERASER) for part in parts[::2]]
    delims = parts[1::2]
    return ''.join(itertools.chain(*itertools.zip_longest(words, delims, fillvalue='')))
