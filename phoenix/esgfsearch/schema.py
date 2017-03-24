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
    constraints = colander.SchemaNode(
        colander.String(),
        default='',
        widget=deform.widget.HiddenWidget(),
    )
    query = colander.SchemaNode(
        colander.String(),
        default=colander.drop,
        # default='*:*',
        widget=deform.widget.HiddenWidget(),
    )
    distrib = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        widget=deform.widget.HiddenWidget(),
    )
    replica = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        widget=deform.widget.HiddenWidget(),
    )
    latest = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        widget=deform.widget.HiddenWidget(),
    )
    temporal = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        widget=deform.widget.HiddenWidget(),
    )
    spatial = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        widget=deform.widget.HiddenWidget(),
    )
    start = colander.SchemaNode(
        colander.Date(),
        default=datetime.date(2001, 1, 1),
        widget=deform.widget.HiddenWidget(),
    )
    end = colander.SchemaNode(
        colander.Date(),
        default=datetime.date(2005, 12, 31),
        widget=deform.widget.HiddenWidget(),
    )
    bbox = colander.SchemaNode(
        colander.String(),
        default='-180,-90,180,90',
        widget=deform.widget.HiddenWidget(),
    )
