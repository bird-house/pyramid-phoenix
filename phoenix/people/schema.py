import colander
import deform

from phoenix.security import Admin, User, Guest

import logging
LOGGER = logging.getLogger("PHOENIX")


class ProfileSchema(deform.schema.CSRFSchema):
    name = colander.SchemaNode(
        colander.String(),
        title="Your Name",
        missing='',
        default='',
    )
    email = colander.SchemaNode(
        colander.String(),
        title="EMail",
        validator=colander.Email(),
        missing=colander.drop,
        widget=deform.widget.TextInputWidget(),
    )
    organisation = colander.SchemaNode(
        colander.String(),
        title="Organisation",
        missing='',
        default='',
    )
    notes = colander.SchemaNode(
        colander.String(),
        title="Notes",
        missing='',
        default=''
    )


class GroupSchema(deform.schema.CSRFSchema):
    choices = ((Admin, 'Admin'), (User, 'User'), (Guest, 'Guest'))

    group = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='Group',
        description='Select Group')


class TokenSchema(deform.schema.CSRFSchema):
    token = colander.SchemaNode(
        colander.String(),
        title="Access Token",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
    token_expires_at = colander.SchemaNode(
        colander.String(),
        title="Expires at",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
