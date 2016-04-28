# -*- coding: utf-8 -*-
import string
import re

from stop_words import get_stop_words


TAG_DELIM_RE = re.compile(r'([.,;()]? +|\.$)')
PUNCT_ERASER = dict.fromkeys(map(ord, string.punctuation + ' '))


def split_tags(tags):
    if not tags:
        return []
    stop_words = get_stop_words('en')
    for tag in TAG_DELIM_RE.split(tags):
        print(tag)
        if tag in stop_words:
            continue
        stripped = tag.strip()
        cleaned = tag.translate(PUNCT_ERASER)
        if stripped and cleaned:
            yield stripped.lower()
