from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class ESGFCredentials(Wizard):
    def __init__(self, request):
        super(ESGFCredentials, self).__init__(
            request,
            name='wizard_esgf_credentials',
            title="ESGF Credentials")

    def schema(self):
        from phoenix.schema import ESGFLoginSchema
        return ESGFLoginSchema()

    def appstruct(self):
        appstruct = super(ESGFCredentials, self).appstruct()
        appstruct['openid'] = self.get_user().get('openid')
        return appstruct

    def success(self, appstruct):
        appstruct['openid'] = self.get_user().get('openid')
        super(ESGFCredentials, self).success(appstruct)

        try:
            self.wizard_state.set('password', appstruct.get('password'))
            from phoenix.models import esgf
            result = esgf.myproxy_logon(
                self.request,
                openid=appstruct.get('openid'),
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
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')
        
    @view_config(route_name='wizard_esgf_credentials', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ESGFCredentials, self).view()
