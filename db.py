# -*- coding: utf-8 -*-
import dataset

import default_settings


def connect():
    return dataset.connect(default_settings.DATASET_DATABASE_URI)


def interviews_table(db=None):
    '''
    Take care not to call multiple times within a single script run.
    '''
    if db is None:
        db = connect()
    return db['interviews']
