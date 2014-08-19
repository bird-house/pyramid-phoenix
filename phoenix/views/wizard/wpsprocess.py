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

class ChooseWPSProcess(Wizard):
    def __init__(self, request):
        super(ChooseWPSProcess, self).__init__(request, 'Choose WPS Process')
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.description = self.wps.identification.title

    def schema(self):
        from phoenix.schema import SelectProcessSchema
        return SelectProcessSchema().bind(processes = self.wps.processes)

    def success(self, appstruct):
        self.wizard_state.set('process_identifier', appstruct.get('identifier'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_literal_inputs')
        
    def appstruct(self):
        return dict(identifier=self.wizard_state.get('process_identifier'))

    def breadcrumbs(self):
        breadcrumbs = super(ChooseWPSProcess, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_literal_inputs', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_process', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPSProcess, self).view()

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
        from webhelpers.html.builder import HTML

        icon_class = "icon-thumbs-down"
        if item['selected'] == True:
            icon_class = "icon-thumbs-up"
        div = Template("""\
        <button class="btn btn-mini select" data-value="${identifier}"><i class="${icon_class}"></i></button>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item['identifier'], 'icon_class': icon_class} )))
    
