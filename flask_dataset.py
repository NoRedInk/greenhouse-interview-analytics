# -*- coding: utf-8 -*-
"""
    flaskext.dataset
    ~~~~~~~~~~~~~~~~~~~
    Simple extension to use Dataset in Flask application.
    :copyright: (c) 2016 by Julien Goret
    :license: MIT
"""
from __future__ import absolute_import, print_function, unicode_literals

import dataset

from flask import _app_ctx_stack as stack
from flask import current_app, has_request_context

from werkzeug.utils import cached_property


__all__ = ['Dataset']


class Dataset(object):
    """Extension object. Behaves as the root object of the database during
    requests.

    ::
        db = Dataset()
        app = Flask(__name__)
        db.init_app(app)

    As a shortcut if you initiate Dataset after Flask you can do this::

        app = Flask(__name__)
        db = Dataset(app)

    """

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Configure a Flask application to use this extension.
        """
        assert 'dataset' not in app.extensions, \
            'app already initiated for dataset'
        app.config.setdefault('DATASET_DATABASE_URI', 'sqlite://')
        app.extensions['dataset'] = _DatasetState(self, app)
        app.teardown_appcontext(self.close)

    def close(self, exception=None):
        """
        Added as a `~flask.Flask.teardown_request` to applications to
        commit the transaction and disconnect from Dataset
        if it was used during the request.
        """
        if self.is_connected:
            if exception is None:
                stack.top.dataset_db.commit()
            else:
                stack.top.dataset_db.rollback()

    @staticmethod
    def connect(app):
        """Create a dataset from the *app* configuration."""
        assert 'DATASET_DATABASE_URI' in app.config, \
            'DATASET_DATABASE_URI not configured'
        return dataset.connect(app.config['DATASET_DATABASE_URI'])

    @property
    def is_connected(self):
        """True if there is a Flask request and Dataset was connected."""
        return hasattr(stack.top, 'dataset_db')

    @property
    def connection(self):
        """Request-bound database connection."""
        assert has_request_context(), \
            'tried to connect to dataset outside request'
        if not self.is_connected:
            connector = current_app.extensions['dataset']
            stack.top.dataset_db = connector.db
        return stack.top.dataset_db

    def __getitem__(self, table_name):
        """
        Get the table from Dataset.
        Exact copy of dataset.Dataset.__getitem__
        """
        return self.connection.get_table(table_name)

    def __getattr__(self, item):
        """
        Get all accessible attributes from the dataset.Database object
        """
        return getattr(self.connection, item)


class _DatasetState(object):
    """Adds a Dataset connection pool to a Flask application."""

    def __init__(self, dataset, app):
        self.dataset = dataset
        self.app = app

    @cached_property
    def db(self):
        """Connection pool."""
        return self.dataset.connect(self.app)
