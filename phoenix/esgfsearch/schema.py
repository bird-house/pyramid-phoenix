import colander
from colander import Invalid
import deform
import datetime

import json


def esgfsearch_validator(node, value):
    search = json.loads(value)
    if search.get('hit-count', 0) > 100:
        raise Invalid(node, 'More than 100 datasets selected: %r.' % search['hit-count'])


class ESGFSearchSchema(colander.MappingSchema):
    facets = colander.SchemaNode(
        colander.String(),
        default='',
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    query = colander.SchemaNode(
        colander.String(),
        default='*:*',
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    distrib = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    replica = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    latest = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    temporal = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    spatial = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
    start = colander.SchemaNode(
        colander.DateTime(),
        default=datetime.datetime(year=2001, month=1, day=1),
        widget=deform.widget.HiddenWidget(),
    )
    end = colander.SchemaNode(
        colander.DateTime(),
        default=datetime.datetime(year=2005, month=12, day=31),
        widget=deform.widget.HiddenWidget(),
    )
    bbox = colander.SchemaNode(
        colander.String(),
        default='-180,-90,180,90',
        missing=colander.null,
        widget=deform.widget.HiddenWidget(),
    )
