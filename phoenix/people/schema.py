import colander
import deform

from phoenix.security import Admin, Developer, User, Guest

import logging
LOGGER = logging.getLogger("PHOENIX")


class ProfileSchema(colander.MappingSchema):
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


class GroupSchema(colander.MappingSchema):
    choices = ((Admin, 'Admin'), (Developer, 'Developer'), (User, 'User'), (Guest, 'Guest'))

    group = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='Group',
        description='Select Group')


class TwitcherSchema(colander.MappingSchema):
    twitcher_token = colander.SchemaNode(
        colander.String(),
        title="Access Token",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
    twitcher_token_expires_at = colander.SchemaNode(
        colander.String(),
        title="Expires at",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )


class ESGFSLCSTokenSchema(colander.MappingSchema):
    esgf_token = colander.SchemaNode(
        colander.String(),
        title="Access Token",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
    esgf_token_expires_at = colander.SchemaNode(
        colander.String(),
        title="Expires at",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )


class ESGFCredentialsSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        title="OpenID",
        description="OpenID to access ESGF data",
        validator=colander.url,
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
    credentials = colander.SchemaNode(
        colander.String(),
        title="Credentials",
        description="URL to ESGF Proxy Certificate",
        validator=colander.url,
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title="Expires at",
        description="When your Proxy Certificate expires",
        missing='',
        widget=deform.widget.TextInputWidget(readonly=True),
    )
