from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class CloudAccess(Wizard):
    def __init__(self, request):
        super(CloudAccess, self).__init__(
            request, name='wizard_cloud', title="Swift Cloud Access")
        self.process = request.wps.describeprocess(identifier='cloud_download')
        self.description = None

    def schema(self):
        from phoenix.wps import WPSSchema
        return WPSSchema(info=False, hide_complex=True, process = self.process)

    def appstruct(self):
        appstruct = super(CloudAccess, self).appstruct()
        appstruct['storage_url'] = self.get_user().get('swift_storage_url')
        appstruct['auth_token'] = self.get_user().get('swift_auth_token')
        return appstruct

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')
    
    @view_config(route_name='wizard_cloud_access', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(CloudAccess, self).view()
    
