# -*- coding: utf-8 -*-
from collections import defaultdict, OrderedDict
import click
import db


REC_SCORES = OrderedDict([
    ('definitely_not', -2),
    ('no', -1),
    ('no_decision', 0),
    ('mixed', 0),
    ('yes', 1),
    ('strong_yes', 2),
])


class KeyValueParamType(click.ParamType):
    name = 'keyvalue'

    def convert(self, value, param, ctx):
        try:
            key, value = value.split('=', 2)
            return (key, value)
        except ValueError:
            self.fail('Must be in key=value format: %s' % value, param, ctx)
KEY_VALUE = KeyValueParamType()


@click.group()
def cli():
    pass


@cli.command()
@click.argument('filters', nargs=-1, type=KEY_VALUE)
def tally_tags(filters):
    table = db.interviews_table()
    tag_recs = defaultdict(lambda: defaultdict(int))
    conditions = [table.table.columns.scorecard_tags != None]
    for column, value in filters:
        conditions.append(getattr(table.table.columns, column) == value)
    for row in table.find(*conditions):
        rec = row['scorecard_recommendation']
        # TODO: maybe aggregate by candidate first
        for tag in split_tags(row['scorecard_tags']):
            tag_recs[tag][rec] += 1
            tag_recs[tag]['score'] += REC_SCORES.get(rec, 0)

    for tag, recs in sorted(tag_recs.items(), key=lambda tag_recs: tag_recs[1]['score']):
        print(tag)
        print(*('{}:{}'.format(rec, recs.get(rec, 0)) for rec in REC_SCORES))
        print()


@cli.command()
@click.argument('column')
def enum_column(column):
    table = db.interviews_table()
    for row in table.distinct(column):
        print(repr(row[column]))


@cli.command()
def columns():
    table = db.interviews_table()
    for column in table.table.columns:
        print(column.name)


if __name__ == '__main__':
    cli()
