# -*- coding: utf-8 -*-
import dataset


db = dataset.connect('sqlite:///data/interviews.db')


def interviews_table():
    return db['interviews']
