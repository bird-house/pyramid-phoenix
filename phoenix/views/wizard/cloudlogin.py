from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class CloudLogin(Wizard):
    def __init__(self, request):
        super(CloudLogin, self).__init__(
            request,
            name='wizard_cloud_login',
            title="Swift Cloud Login")

    def schema(self):
        from phoenix.schema import CloudLoginSchema
        return CloudLoginSchema().bind()

    def success(self, appstruct):
        super(CloudLogin, self).success(appstruct)

        try:
            from phoenix.models import cloud_logon
            result = cloud_logon(
                self.request,
                username = appstruct.get('username'),
                password = appstruct.get('password'))

            user = self.get_user()
            user['swift_storage_url'] = result['storage_url']
            user['swift_auth_token'] = result['auth_token'] 
            self.userdb.update({'email':self.user_email()}, user)
        except Exception, e:
            logger.exception("update cloud token failed.")
            self.request.session.flash(
                "Could not update your cloud token. %s" % (e), queue='error')
        else:
            self.request.session.flash(
                'Cloud token updated.', queue='success')
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_cloud_access')
        
    @view_config(route_name='wizard_cloud_login', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(CloudLogin, self).view()
