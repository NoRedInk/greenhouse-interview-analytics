# -*- coding: utf-8 -*-


def iter_tags(text, tags_prefix=None, tag_delim=','):
    '''
    >>> list(find_tags('tags: foo-bar, baz\\nxyzzy', tags_prefix='tags:'))
    ['foo-bar', 'baz']
    '''
    if not text:
        return []
    for line in text.splitlines():
        if tags_prefix and not line.startswith(tags_prefix):
            continue
        for tag in line[len(tags_prefix or ''):].split(tag_delim):
            cleaned = tag.strip()
            if cleaned:
                yield cleaned
