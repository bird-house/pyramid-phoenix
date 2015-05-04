from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class ChooseWPSProcess(Wizard):
    def __init__(self, request):
        super(ChooseWPSProcess, self).__init__(
            request,
            name='wizard_process',
            title='Choose WPS Process')
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(self.wizard_state.get('wizard_wps')['url'])
        self.description = self.wps.identification.title

    def schema(self):
        from phoenix.schema import SelectProcessSchema
        return SelectProcessSchema().bind(processes = self.wps.processes)

    def next_success(self, appstruct):
        self.success(appstruct)

        # TODO: this code does not belong here
        from phoenix.wps import count_literal_inputs
        identifier = appstruct['identifier']
        if count_literal_inputs(self.wps, identifier) > 0:
            return self.next('wizard_literal_inputs')
        self.wizard_state.set('wizard_literal_inputs', {})
        return self.next('wizard_complex_inputs')
        
    @view_config(route_name='wizard_process', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPSProcess, self).view()

from phoenix.grid import MyGrid
from string import Template

class CatalogSearchGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(CatalogSearchGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['selected'] = self.selected_td
        self.column_formats['title'] = self.title_td
        self.column_formats['format'] = self.format_td
        self.column_formats['modified'] = self.modified_td

    def title_td(self, col_num, i, item):
        return self.render_title_td(item['title'], item['abstract'], item.get('subjects'))

    def format_td(self, col_num, i, item):
        return self.render_format_td(item['format'], item['source'])

    def modified_td(self, col_num, i, item):
        return self.render_timestamp_td(timestamp=item.get('modified'))

    def selected_td(self, col_num, i, item):
        from string import Template
        from webhelpers2.html.builder import HTML

        icon_class = "glyphicon glyphicon-thumbs-down"
        if item['selected'] == True:
            icon_class = "glyphicon glyphicon-thumbs-up"
        div = Template("""\
        <button class="btn btn-mini select" data-value="${identifier}"><i class="${icon_class}"></i></button>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item['identifier'], 'icon_class': icon_class} )))
    
