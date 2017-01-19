import deform
import colander
from colander import Invalid

from phoenix.security import Admin, User, Guest

import logging
logger = logging.getLogger(__name__)


class AuthProtocolSchema(colander.MappingSchema):
    choices = [
        ('phoenix', 'Local Auth'),
        ('esgf', 'ESGF OpenID'),
        ('openid', 'OpenID'),
        ('oauth2', 'OAuth 2.0'),
        ('ldap', 'LDAP')]

    auth_protocol = colander.SchemaNode(
        colander.Set(),
        default=['phoenix', ],
        title='Authentication Protocol',
        description='Choose at least one Authentication Protocol which is used in Phoenix.',
        validator=colander.Length(min=1),
        widget=deform.widget.CheckboxChoiceWidget(values=choices, inline=True))


class LdapSchema(colander.MappingSchema):
    server = colander.SchemaNode(
        colander.String(),
        title='Server',
        validator=colander.url,
        description='URI of LDAP server to connect to, e.g. "ldap://ldap.example.com"')
    use_tls = colander.SchemaNode(
        colander.Boolean(),
        title='Use TLS',
        description='Activate TLS when connecting',
        widget=deform.widget.CheckboxWidget())
    bind = colander.SchemaNode(
        colander.String(),
        title='Bind',
        description='Bind to use for the LDAP connection, e.g. "CN=admin,DC=example,DC=com".'
                    ' Leave empty for anonymous bind.',
        missing='')
    passwd = colander.SchemaNode(
        colander.String(),
        title='Password',
        description='Password for the LDAP bind. Leave empty for anonymous bind.',
        widget=deform.widget.PasswordWidget(),
        missing='')
    base_dn = colander.SchemaNode(
        colander.String(),
        title='Base DN',
        description='DN where to begin the search for users, e.g. "CN=Users,DC=example,DC=com"')
    filter_tmpl = colander.SchemaNode(
        colander.String(),
        title='LDAP filter',
        description="""Is used to filter the LDAP search.
                    Should always contain the placeholder "%(login)s".
                    Example for OpenLDAP: "(uid=%(login)s)";
                    Example for MS AD: "(sAMAccountName=%(login)s)".
                    Have a look at http://pyramid-ldap.readthedocs.org/en/latest/
                    for more information.""")
    scope = colander.SchemaNode(
        colander.String(),
        title='Scope',
        description='Scope to search in',
        widget=deform.widget.SelectWidget(values=(
            ('ONELEVEL', 'One level'),
            ('SUBTREE', 'Subtree')))
    )
    name = colander.SchemaNode(
        colander.String(),
        title='User name attribute',
        description='Optional: LDAP attribute to receive user name from query, e.g. "cn"',
        missing='')
    email = colander.SchemaNode(
        colander.String(),
        title='User e-mail attribute',
        description='Optional: LDAP attribute to receive user e-mail from query, e.g. "mail"',
        missing='')


class GitHubSchema(colander.MappingSchema):
    github_client_id = colander.SchemaNode(
        colander.String(),
        title='GitHub Client ID',
        description="Register at GitHub: https://github.com/settings/applications/new",
        validator=colander.Length(min=20),
    )
    github_client_secret = colander.SchemaNode(
        colander.String(),
        title='GitHub Client Secret',
        validator=colander.Length(min=20),
    )


class ESGFSLCSSchema(colander.MappingSchema):
    esgf_slcs_url = colander.SchemaNode(
        colander.String(),
        title='URL of ESGF SLCS Service',
        validator=colander.url,
    )
    esgf_slcs_client_id = colander.SchemaNode(
        colander.String(),
        title='ESGF SLCS Client ID',
        validator=colander.Length(min=20),
    )
    esgf_slcs_client_secret = colander.SchemaNode(
        colander.String(),
        title='ESGF SLCS Client Secret',
        validator=colander.Length(min=20),
    )
