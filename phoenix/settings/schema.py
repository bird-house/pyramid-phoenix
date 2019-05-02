import deform
from deform.widget import OptGroup
import colander

from phoenix.security import AUTH_PROTOCOLS

import logging
LOGGER = logging.getLogger("PHOENIX")


@colander.deferred
def deferred_processes_widget(node, kw):
    processes = kw.get('processes', [])
    choices = [('', "Select up to six public processes you'd like to show.")]
    for group in list(processes.keys()):
        options = []
        for process in processes[group]:
            option = "{}.{}".format(group, process)
            options.append((option, process))
        choices.append(OptGroup(group, *options))
    return deform.widget.Select2Widget(values=choices, multiple=True)


class ProcessesSchema(deform.schema.CSRFSchema):
    pinned_processes = colander.SchemaNode(
        colander.Set(),
        widget=deferred_processes_widget,
        validator=colander.Length(min=0, max=6)
    )


class AuthProtocolSchema(deform.schema.CSRFSchema):
    choices = list(AUTH_PROTOCOLS.items())

    auth_protocol = colander.SchemaNode(
        colander.Set(),
        default=['phoenix'],
        title='Authentication Protocol',
        description='Choose at least one Authentication Protocol which is used in Phoenix.',
        validator=colander.Length(min=1),
        widget=deform.widget.CheckboxChoiceWidget(values=choices, inline=True))


class LdapSchema(deform.schema.CSRFSchema):
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
