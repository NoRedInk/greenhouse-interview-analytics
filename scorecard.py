# -*- coding: utf-8 -*-
import re

import tagging


def extract_tags(questions, tags_prefix=None, question_title_re=None):
    '''
    >>> questions = [{'id': None, 'question': 'What was the question?', 'answer': 'default, tags'}]
    >>> set(['default', 'tags']) == extract_tags(questions)
    True
    '''
    tags = set()
    for answer in iter_answers(questions, question_title_re):
        tags |= set(tagging.iter_tags(answer, tags_prefix=tags_prefix))
    return tags


def iter_answers(questions, question_title_re=None):
    '''
    >>> questions = [{'id': None, 'question': 'What was the question?', 'answer': 42}]
    >>> list(iter_answers(questions, 'What was'))
    [42]
    '''
    for question in questions:
        if question_title_re and not re.match(question_title_re, question['question']):
            continue
        yield question['answer']
