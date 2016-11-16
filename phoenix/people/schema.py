import colander
import deform

from phoenix.security import Admin, User, Guest

import logging
logger = logging.getLogger(__name__)


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
    choices = ((Admin, 'Admin'), (User, 'User'), (Guest, 'Guest'))

    group = colander.SchemaNode(
         colander.String(),
         validator=colander.OneOf([x[0] for x in choices]),
         widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
         title='Group',
         description='Select Group')


class TwitcherSchema(colander.MappingSchema):
    twitcher_token = colander.SchemaNode(
        colander.String(),
        title="Twitcher access token",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    twitcher_token_expires = colander.SchemaNode(
        colander.String(),
        title="Expires",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )


class C4ISchema(colander.MappingSchema):
    c4i_token = colander.SchemaNode(
        colander.String(),
        title="C4I access token",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    c4i_token_expires = colander.SchemaNode(
        colander.String(),
        title="Expires",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )


class ESGFCredentialsSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        title="OpenID",
        description="OpenID to access ESGF data",
        validator=colander.url,
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    credentials = colander.SchemaNode(
        colander.String(),
        title="Credentials",
        description="URL to ESGF Proxy Certificate",
        validator=colander.url,
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title="Expires",
        description="When your Proxy Certificate expires",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )




