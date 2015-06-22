import deform
import colander
from colander import Invalid

from phoenix.widget import (
    TagsWidget,
    ESGFSearchWidget,
    )

import logging
logger = logging.getLogger(__name__)


class PhoenixSchema(colander.MappingSchema):
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Enter the Phoenix Password',
        validator = colander.Length(min=8),
        widget = deform.widget.PasswordWidget())

class OAuthSchema(colander.MappingSchema):
    choices = [('github', 'GitHub')]
    
    provider = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='OAuth 2.0 Provider',
        description='Select your OAuth Provider.')

class OpenIDSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        validator = colander.url,
        title = "OpenID",
        description = "Example: https://esgf-data.dkrz.de/esgf-idp/openid/myname or https://openid.stackexchange.com/",
        default = 'https://openid.stackexchange.com/')
        
class ESGFOpenIDSchema(colander.MappingSchema):
    from phoenix.security import ESGF_Provider
    choices = zip(ESGF_Provider.keys(), ESGF_Provider.keys())
    provider = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='ESGF Provider',
        description='Select the Provider for your ESGF OpenID.')
    username = colander.SchemaNode(
        colander.String(),
        validator = colander.Length(min=6),
        title = "Username",
        description = "Your ESGF OpenID Username."
        )

class ESGFLoginSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "Type your OpenID from your ESGF provider",
        validator = colander.url
        )
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Type your password for your ESGF OpenID',
        validator = colander.Length(min=6),
        widget = deform.widget.PasswordWidget())

class SwiftLoginSchema(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(),
        title = "Username",
        description = "Your Swift Username: account:user",
        missing = '',
        default = '',
        )
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        missing = '',
        default = '',
        widget = deform.widget.PasswordWidget(size=30))

class LdapSchema(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(),
        title = "Username",
        description = "Your username",
        )
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Your password',
        widget = deform.widget.PasswordWidget())

class UserProfileSchema(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(),
        title = "Your Name",
        missing = '',
        default = '',
        )
    email = colander.SchemaNode(
        colander.String(),
        title = "EMail",
        validator = colander.Email(),
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        missing = '',
        default = '',
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        missing = '',
        default = '',
        )

class ESGFCredentialsSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "OpenID to access ESGF data",
        validator = colander.url,
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    credentials = colander.SchemaNode(
        colander.String(),
        title = "Credentials",
        description = "URL to ESGF Proxy Certificate",
        validator = colander.url,
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title = "Expires",
        description = "When your Proxy Certificate expires",
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )

class SwiftSchema(colander.MappingSchema):
    swift_username = colander.SchemaNode(
        colander.String(),
        title = "Swift Username",
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    swift_storage_url = colander.SchemaNode(
        colander.String(),
        title = "Swift Storage URL",
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    swift_auth_token = colander.SchemaNode(
        colander.String(),
        title = "Swift Auth Token",
        missing = '',
        widget = deform.widget.TextInputWidget(template='readonly/textinput'),
        )

def esgfsearch_validator(node, value):
    import json
    search = json.loads(value)
    if search.get('hit-count', 0) > 100:
        raise Invalid(node, 'More than 100 datasets selected: %r.' %  search['hit-count'])

class ESGFSearchSchema(colander.MappingSchema):
    selection = colander.SchemaNode(
        colander.String(),
        validator = esgfsearch_validator,
        title = 'ESGF Search',
        widget = ESGFSearchWidget(url="/esg-search"))

class DoneSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_favorite_name(node, kw):
        return kw.get('favorite_name', 'test')
    
    is_favorite = colander.SchemaNode(
        colander.Boolean(),
        title = "Save as Favorite",
        default = False,
        missing= False)
    favorite_name = colander.SchemaNode(
        colander.String(),
        title = "Favorite Name",
        default = deferred_favorite_name)

class UploadSchema(SwiftLoginSchema):
    
    container = colander.SchemaNode(colander.String())
    prefix = colander.SchemaNode(colander.String())
    #object_name = colander.SchemaNode(colander.String())
    source = colander.SchemaNode(
        colander.String(),
        description = 'URL to the source',
        validator = colander.url)

class PublishSchema(colander.MappingSchema):
    import uuid

    @colander.deferred
    def deferred_default_creator(node, kw):
        return kw.get('email')

    @colander.deferred
    def deferred_default_format(node, kw):
        return kw.get('format', "application/x-netcdf")
        
    identifier = colander.SchemaNode(
        colander.String(),
        default = uuid.uuid4().get_urn())
    title = colander.SchemaNode(colander.String())
    abstract = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        validator = colander.Length(max=150),
        widget = deform.widget.TextAreaWidget(rows=2, cols=80))
    creator = colander.SchemaNode(
        colander.String(),
        validator = colander.Email(),
        default = deferred_default_creator,)
    source = colander.SchemaNode(
        colander.String(),
        description = 'URL to the source',
        validator = colander.url)
    format = colander.SchemaNode(
        colander.String(),
        default = deferred_default_format,
        description = 'Format of your source. Example: NetCDF',
        )
    subjects = colander.SchemaNode(
        colander.String(),
        default = 'test',
        missing = 'test',
        description = "Keywords: tas, temperature, ...",
        widget = TagsWidget(),
        )
    rights = colander.SchemaNode(
        colander.String(),
        missing = 'Unknown',
        default = 'Free for non-commercial use',
        )



