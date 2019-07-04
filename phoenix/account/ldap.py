import colander
import deform

from pyramid.view import view_config

from phoenix.account.base import Account

import logging
LOGGER = logging.getLogger("PHOENIX")


class LDAPSchema(deform.schema.CSRFSchema):
    username = colander.SchemaNode(
        colander.String(),
        title="Username",
    )
    password = colander.SchemaNode(
        colander.String(),
        title='Password',
        widget=deform.widget.PasswordWidget())


class LDAPAccount(Account):
    def schema(self):
        return LDAPSchema().bind(request=self.request)

    def _handle_appstruct(self, appstruct):
        """
        Handle LDAP login.
        """
        username = self.request.params.get('username')
        password = self.request.params.get('password')

        # Performing ldap login
        from pyramid_ldap import get_ldap_connector
        connector = get_ldap_connector(self.request)
        auth = connector.authenticate(username, password)

        if auth is not None:
            # Get user name and email
            ldap_settings = self.request.db.ldap.find_one()
            name = (auth[1].get(ldap_settings['name'])[0] if ldap_settings['name'] != '' else 'Unknown')
            email = (auth[1].get(ldap_settings['email'])[0] if ldap_settings['email'] != '' else '')

            # Authentication successful
            return self.login_success(login_id=auth[0], name=name, email=email)  # login_id=user_dn
        else:
            # Authentification failed
            return self.login_failure()

    @view_config(route_name='ldap_login', renderer='phoenix:account/templates/account/login.pt')
    def ldap_login(self):
        self.init_ldap()
        return self.login()

    def init_ldap(self):
        """Lazy LDAP connector construction"""
        if not self.request.ldap_activated:
            # Warn if LDAP is about to be used but not set up.
            self.session.flash('<strong>Error</strong>:LDAP does not seem to be set up correctly!', queue='danger')
        elif getattr(self.request, 'ldap_connector', None) is None:
            LOGGER.debug('Set up LDAP connector...')
            ldap_settings = self.request.db.ldap.find_one()

            # Set LDAP settings
            from . import ldap
            if ldap_settings['scope'] == 'ONELEVEL':
                ldap_scope = ldap.SCOPE_ONELEVEL
            else:
                ldap_scope = ldap.SCOPE_SUBTREE

            # FK: Do we have to think about race conditions here?
            from pyramid.config import Configurator
            config = Configurator(registry=self.request.registry)
            config.ldap_setup(ldap_settings['server'],
                              bind=ldap_settings['bind'],
                              passwd=ldap_settings['passwd'])
            config.ldap_set_login_query(
                base_dn=ldap_settings['base_dn'],
                filter_tmpl=ldap_settings['filter_tmpl'],
                scope=ldap_scope)
            config.commit()
