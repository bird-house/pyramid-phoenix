from pyramid.view import view_config

from phoenix.account.views import Account
from phoenix.account.schema import LdapSchema


class LDAPAccount(Account):
    def schema(self):
        return LdapSchema()

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

    @view_config(route_name='ldap_login', renderer='templates/account/login.pt')
    def login(self):
        self.ldap_prepare()
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(form=form.render(self.appstruct()))

    def ldap_prepare(self):
        """Lazy LDAP connector construction"""
        ldap_settings = self.request.db.ldap.find_one()

        if ldap_settings is None:
            # Warn if LDAP is about to be used but not set up.
            self.session.flash('LDAP does not seem to be set up correctly!', queue='danger')
        elif getattr(self.request, 'ldap_connector', None) is None:
            LOGGER.debug('Set up LDAP connector...')

            # Set LDAP settings
            import ldap
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
