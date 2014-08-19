from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from deform import Form, Button

from owslib.wps import WebProcessingService

from string import Template

from phoenix import models
from phoenix.views import MyView
from phoenix.grid import MyGrid
from phoenix.views.wizard import Wizard
from phoenix.exceptions import MyProxyLogonFailure

import logging
logger = logging.getLogger(__name__)

class ESGFCredentials(Wizard):
    def __init__(self, request):
        super(ESGFCredentials, self).__init__(
            request,
            "ESGF Credentials",
            "")

    def schema(self):
        from phoenix.schema import CredentialsSchema
        return CredentialsSchema().bind()

    def success(self, appstruct):
        try:
            self.wizard_state.set('password', appstruct.get('password'))
            result = models.myproxy_logon(
                self.request,
                openid=self.get_user().get('openid'),
                password=appstruct.get('password'))
            user = self.get_user()
            user['credentials'] = result['credentials']
            user['cert_expires'] = result['cert_expires'] 
            self.userdb.update({'email':self.user_email()}, user)
        except Exception, e:
            logger.exception("update credentials failed.")
            self.request.session.flash(
                "Could not update your credentials. %s" % (e), queue='error')
        else:
            self.request.session.flash(
                'Credentials updated.', queue='success')
        
    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_check_parameters')
        
    def appstruct(self):
        return dict(
            openid=self.get_user().get('openid'),
            password=self.wizard_state.get('password'))

    def breadcrumbs(self):
        breadcrumbs = super(ESGFCredentials, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_esgf_credentials', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_esgf_credentials', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFCredentials, self).view()
