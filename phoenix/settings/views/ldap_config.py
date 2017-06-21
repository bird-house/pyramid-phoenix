from pyramid.view import view_config, view_defaults
from deform import Form, ValidationFailure

from phoenix.views import MyView

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='admin', layout='default', require_csrf=False)
class Ldap(MyView):
    def __init__(self, request):
        super(Ldap, self).__init__(request, name='settings_ldap', title='LDAP')

    def breadcrumbs(self):
        breadcrumbs = super(Ldap, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings'), title="Settings"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='settings_ldap', renderer='../templates/settings/ldap.pt')
    def view(self):
        # Get LDAP settings
        ldap_settings = self.request.db.ldap.find_one()
        if ldap_settings is None:
            ldap_settings = dict()

        # Generate form
        from phoenix.settings.schema import LdapSchema
        ldap_form = Form(schema=LdapSchema(), buttons=('submit',), formid='deform')

        if 'submit' in self.request.params:
            try:
                # Validate form
                appstruct = ldap_form.validate(self.request.params.items())
            except ValidationFailure, e:
                LOGGER.exception('Validation failed!')
                return dict(title='LDAP Settings', form=e.render())
            else:
                # Update LDAP settings
                ldap_settings['server'] = appstruct['server']
                ldap_settings['use_tls'] = appstruct['use_tls']
                ldap_settings['bind'] = appstruct['bind']
                ldap_settings['passwd'] = appstruct['passwd']
                ldap_settings['base_dn'] = appstruct['base_dn']
                ldap_settings['filter_tmpl'] = appstruct['filter_tmpl']
                ldap_settings['scope'] = appstruct['scope']
                # Optional:
                ldap_settings['name'] = appstruct['name']
                ldap_settings['email'] = appstruct['email']
                self.request.db.ldap.save(ldap_settings)

                import ldap
                if ldap_settings['scope'] == 'ONELEVEL':
                    ldap_scope = ldap.SCOPE_ONELEVEL
                else:
                    ldap_scope = ldap.SCOPE_SUBTREE

                from pyramid.config import Configurator
                config = Configurator(registry=self.request.registry)
                config.ldap_setup(
                    ldap_settings['server'],
                    bind=ldap_settings['bind'],
                    passwd=ldap_settings['passwd'],
                    use_tls=ldap_settings['use_tls'])
                config.ldap_set_login_query(
                    base_dn=ldap_settings['base_dn'],
                    filter_tmpl=ldap_settings['filter_tmpl'],
                    scope=ldap_scope)
                config.commit()

                self.session.flash('Successfully updated LDAP settings!', queue='success')

        # Display form
        return dict(title='LDAP Settings', form=ldap_form.render(ldap_settings))
