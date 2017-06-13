import colander
from colander import Invalid
import deform
import datetime

import json


class ESGFLogonSchema(colander.MappingSchema):
    choices = (
        ('slcs1.ceda.ac.uk', 'CEDA (England)'),
        ('esgf-data.dkrz.de', 'DKRZ (Hamburg, Germany)'),
        ('esgf-node.ipsl.upmc.fr', 'IPSL (Paris, France)'),
        # ('pcmdi.llnl.gov', 'PCMDI'),
        # ('esg-dn1.nsc.liu.se', 'SMHI'),
    )

    provider = colander.SchemaNode(
        colander.String(),
        title="Provider",
        description="Choose your ESGF provider.",
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices,
                                               inline=True),
        default='esgf-data.dkrz.de',
    )
    username = colander.SchemaNode(
        colander.String(),
        title="Username",
        description="Type your username for your ESGF account.",
        validator=colander.Length(min=2),
    )
    password = colander.SchemaNode(
        colander.String(),
        title='Password',
        description='Type your password for your ESGF account.',
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget())


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
        default='',
        missing='',
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
