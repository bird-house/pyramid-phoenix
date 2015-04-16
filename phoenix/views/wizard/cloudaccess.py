from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class CloudAccess(Wizard):
    def __init__(self, request):
        super(CloudAccess, self).__init__(
            request, name='wizard_cloud_access', title="Swift Cloud Access")
        self.process = request.wps.describeprocess(identifier='cloud_download')
        self.description = None

    def schema(self):
        from phoenix.schema import CloudAccessSchema
        return CloudAccessSchema().bind(container=['MyTest'])

    def appstruct(self):
        appstruct = super(CloudAccess, self).appstruct()
        #appstruct['container'] = ['MyTest']
        return appstruct

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')
    
    @view_config(route_name='wizard_cloud_access', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(CloudAccess, self).view()
    
