from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import SettingsView
from deform import Form, ValidationFailure

import logging
logger = logging.getLogger(__name__)

class Ldap(SettingsView):
    def __init__(self, request):
        super(Ldap, self).__init__(request, name='settings_ldap', title='LDAP')

    def breadcrumbs(self):
        breadcrumbs = super(Ldap, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='settings_ldap', renderer='../templates/settings/ldap.pt')
    def view(self):
        # Get LDAP settings
        ldap_settings = self.db.ldap.find_one()
        if ldap_settings is None:
            ldap_settings = {'server': '', 'bind': '', 'passwd': ''}

        # Generate form
        from phoenix.schema.settings import LdapSchema
        ldap_form = Form(schema = LdapSchema(), buttons = ('submit',), formid = 'deform')

        if 'submit' in self.request.params:
            try:
                # Validate form
                appstruct = ldap_form.validate(self.request.params.items())
            except ValidationFailure, e:
                logger.exception('Validation failed!')
                return dict(title = 'LDAP Settings', form = e.render())
            else:
                # Update LDAP settings
                ldap_settings['server'] = appstruct['server']
                ldap_settings['bind']   = appstruct['bind']
                ldap_settings['passwd'] = appstruct['passwd']
                self.db.ldap.save(ldap_settings)
                self.session.flash('Successfully updated LDAP settings!', queue = 'success')

        # Display form
        return dict(title = 'LDAP Settings', form = ldap_form.render(ldap_settings))
