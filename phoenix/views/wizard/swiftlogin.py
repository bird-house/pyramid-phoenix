from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class SwiftLogin(Wizard):
    def __init__(self, request):
        super(SwiftLogin, self).__init__(
            request,
            name='wizard_swift_login',
            title="Swift Cloud Login")

    def breadcrumbs(self):
        breadcrumbs = super(SwiftLogin, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        from phoenix.schema import SwiftLoginSchema
        return SwiftLoginSchema().bind()

    def appstruct(self):
        appstruct = super(SwiftLogin, self).appstruct()
        user = self.get_user()
        appstruct['username'] = appstruct.get('username', user.get('swift_username'))
        return appstruct

    def login(self, appstruct):
        from phoenix.models import swift
        result = swift.swift_login(
            self.request,
            username = appstruct.get('username'),
            password = appstruct.get('password'))

        user = self.get_user()
        user['swift_username'] = appstruct.get('username')
        user['swift_storage_url'] = result['storage_url']
        user['swift_auth_token'] = result['auth_token'] 
        self.userdb.update({'email':self.user_email()}, user)
        
    def next_success(self, appstruct):
        try:
            self.login(appstruct)
        except Exception, e:
            logger.exception("update of swift token failed.")
            return self.flash_error("Could not update your Swift token. %s" % (e))
        else:
            super(SwiftLogin, self).success(appstruct)
            self.flash_success('Swift token was updated.')
            return self.next('wizard_swiftbrowser')
        
    @view_config(route_name='wizard_swift_login', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(SwiftLogin, self).view()
