from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class ESGFSearch(Wizard):
    def __init__(self, request):
        super(ESGFSearch, self).__init__(request, name='wizard_esgf', title="ESGF Search")

    def schema(self):
        from phoenix.schema import ESGFSearchSchema
        return ESGFSearchSchema()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_esgf_files')

    @view_config(route_name='wizard_esgf', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFSearch, self).view()
