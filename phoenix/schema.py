import colander
import deform

from .widget import TagsWidget

class CredentialsSchema(colander.MappingSchema):
    """
    ESGF user credentials schema
    """
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "OpenID from your ESGF provider",
        validator = colander.url,
        missing = '',
        default = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Password for this OpenID',
        missing = '',
        default = '',
        widget = deform.widget.PasswordWidget(size=20))

class AccountSchema(colander.MappingSchema):
    """
    User account schema
    """
    name = colander.SchemaNode(
        colander.String(),
        title = "Name",
        description = "Your Name",
        missing = '',
        default = '',
        )
    email = colander.SchemaNode(
        colander.String(),
        title = "EMail",
        description = "eMail used for login",
        validator = colander.Email(),
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "OpenID to access ESGF data",
        validator = colander.url,
        missing = '',
        default = '',
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        description = "Your Organisation",
        missing = '',
        default = '',
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        description = "Some Notes about you",
        missing = '',
        default = '',
        )
    token = colander.SchemaNode(
        colander.String(),
        title = "Token",
        description = "Access Token",
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    credentials = colander.SchemaNode(
        colander.String(),
        title = "Credentials",
        description = "URL to ESGF Proxy Certificate",
        validator = colander.url,
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title = "Expires",
        description = "When your Proxy Certificate expires",
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )

@colander.deferred
def deferred_wps_list_widget(node, kw):
    wps_list = kw.get('wps_list', [])
    return deform.widget.RadioChoiceWidget(values=wps_list)

class SelectWPSSchema(colander.MappingSchema):
   
    url = colander.SchemaNode(
        colander.String(),
        title = 'WPS',
        description = "Select WPS",
        widget = deferred_wps_list_widget
        )

class CatalogSchema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        title = 'URL',
        description = 'Add WPS URL',
        missing = '',
        default = '',
        validator = colander.url,
        widget = deform.widget.TextInputWidget())

    notes = colander.SchemaNode(
        colander.String(),
        title = 'Notes',
        description = 'Add some notes for this WPS',
        missing = '',
        default = '',
        widget = deform.widget.TextInputWidget())


class PublishSchema(colander.MappingSchema):
    title = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(),
        )
    abstract = colander.SchemaNode(
        colander.String(),
        validator = colander.Length(max=150),
        widget = deform.widget.TextAreaWidget(rows=2, cols=80),
        )
    author = colander.SchemaNode(
        colander.String(),
        validator = colander.Email(),
        widget=deform.widget.TextInputWidget(),
        )
    url = colander.SchemaNode(
        colander.String(),
        title = 'URL',
        validator = colander.url,
        widget = deform.widget.TextInputWidget())
    mime_type = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(),
        )
    keywords = colander.SchemaNode(
        colander.String(),
        default = 'test',
        missing = 'test',
        widget = TagsWidget(),
        )
            
class UserSchema(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(),
        title = "Name",
        missing = colander.drop,
        )
    user_id = colander.SchemaNode(
        colander.String(),
        title = "eMail",
        validator = colander.Email(),
        widget=deform.widget.TextInputWidget(),
        )
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        validator = colander.url,
        missing = colander.drop,
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        missing = colander.drop,
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        missing = colander.drop,
        )


