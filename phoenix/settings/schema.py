import deform
import colander
from colander import Invalid

from phoenix.security import Admin, User, Guest
from phoenix.schema import UserProfileSchema

import logging
logger = logging.getLogger(__name__)

class EditUserSchema(UserProfileSchema):
    choices = ((Admin, 'Admin'), (User, 'User'), (Guest, 'Guest'))
    
    group = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='Group',
        description='Select Group')

class AuthSchema(colander.MappingSchema):
    choices = [
        ('esgf', 'ESGF OpenID'),
        ('openid', 'OpenID'),
        ('oauth2', 'OAuth 2.0'),
        ('ldap', 'LDAP')]

    protocol = colander.SchemaNode(
        colander.Set(),
        default = ['oauth2'],
        title='Auth Protocol',
        description='Choose at least one Authentication Protocol which is used in Phoenix',
        validator=colander.Length(min=1),
        widget=deform.widget.CheckboxChoiceWidget(values=choices, inline=True))

class LdapSchema(colander.MappingSchema):
    server = colander.SchemaNode(
            colander.String(),
            title = 'Server',
            validator = colander.url,
            description = 'URI of LDAP server to connect to, e.g. "ldap://ldap.example.com"')
    bind = colander.SchemaNode(
            colander.String(),
            title = 'Bind',
            description = 'Bind to use for the LDAP connection, e.g. "CN=admin,DC=example,DC=com"')
    passwd = colander.SchemaNode(
            colander.String(),
            title = 'Password',
            description = 'Password for the LDAP bind',
            widget = deform.widget.PasswordWidget())
    base_dn = colander.SchemaNode(
            colander.String(),
            title = 'Base DN',
            description = 'DN where to begin the search for users, e.g. "CN=Users,DC=example,DC=com"')
    filter_tmpl = colander.SchemaNode(
            colander.String(),
            title = 'LDAP filter',
            description = """Is used to filter the LDAP search.
                    Should always contain the placeholder "%(login)s".
                    Example for OpenLDAP: "(uid=%(login)s)"
                    Example for MS AD:    "(sAMAccountName=%(login)s)"
                    Have a look at http://pyramid-ldap.readthedocs.org/en/latest/
                    for more information.""")
    scope = colander.SchemaNode(
            colander.String(),
            title = 'Scope',
            description = 'Scope to search in',
            widget = deform.widget.SelectWidget(values = (
                ('ONELEVEL', 'One level'),
                ('SUBTREE',  'Subtree')))
            )
    name = colander.SchemaNode(
            colander.String(),
            title = 'User name attribute',
            description = 'Optional: LDAP attribute to receive user name from query, e.g. "cn"',
            missing = '')
    email = colander.SchemaNode(
            colander.String(),
            title = 'User e-mail attribute',
            description = 'Optional: LDAP attribute to receive user e-mail from query, e.g. "mail"',
            missing = '')
