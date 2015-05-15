from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class ESGFLogin(Wizard):
    def __init__(self, request):
        super(ESGFLogin, self).__init__(
            request,
            name='wizard_esgf_login',
            title="ESGF Login")

    def breadcrumbs(self):
        breadcrumbs = super(ESGFLogin, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        from phoenix.schema import ESGFLoginSchema
        return ESGFLoginSchema()

    def appstruct(self):
        appstruct = super(ESGFLogin, self).appstruct()
        appstruct['openid'] = self.get_user().get('openid')
        return appstruct

    def success(self, appstruct):
        appstruct['openid'] = self.get_user().get('openid')
        super(ESGFLogin, self).success(appstruct)

        self.wizard_state.set('password', appstruct.get('password'))
        from phoenix.tasks import myproxy_logon
        myproxy_logon.delay(self.user_email(), self.request.wps.url, 
                            appstruct.get('openid'),
                            appstruct.get('password'))
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')
        
    @view_config(route_name='wizard_esgf_login', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ESGFLogin, self).view()
