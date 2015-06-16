from pyramid.view import view_config
import colander
import deform

from phoenix.wizard.views import Wizard
from phoenix.catalog import wps_url

def count_literal_inputs(wps, identifier):
    process = wps.describeprocess(identifier)
    literal_inputs = []
    for input in process.dataInputs:
        if input.dataType != 'ComplexData':
            literal_inputs.append(input)
    return len(literal_inputs)

class Schema(colander.MappingSchema):
    @colander.deferred
    def deferred_validator(node, kw):
        wps = kw.get('wps')

        choices = []
        for process in wps.processes:
            choices.append(process.identifier)
        return colander.OneOf(choices)
    
    @colander.deferred
    def deferred_widget(node, kw):
        wps = kw.get('wps')

        choices = []
        for process in wps.processes:
            desc = process.title
            if hasattr(process, 'abstract'):
                desc = "{0.title} - {0.abstract}".format(process)
            choices.append( (process.identifier, desc) )
        return deform.widget.RadioChoiceWidget(values = choices)

    identifier = colander.SchemaNode(
        colander.String(),
        title = "Process",
        validator = deferred_validator,
        widget = deferred_widget)

class ChooseWPSProcess(Wizard):
    def __init__(self, request):
        super(ChooseWPSProcess, self).__init__(
            request,
            name='wizard_process',
            title='Choose WPS Process')
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(wps_url(request, self.wizard_state.get('wizard_wps')['identifier']))
        self.title = "Choose WPS Process of {0}".format(self.wps.identification.title)

    def breadcrumbs(self):
        breadcrumbs = super(ChooseWPSProcess, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema().bind(wps=self.wps)

    def next_success(self, appstruct):
        self.success(appstruct)

        # TODO: this code does not belong here
        identifier = appstruct['identifier']
        if count_literal_inputs(self.wps, identifier) > 0:
            return self.next('wizard_literal_inputs')
        self.wizard_state.set('wizard_literal_inputs', {})
        return self.next('wizard_complex_inputs')
        
    @view_config(route_name='wizard_process', renderer='../templates/wizard/default.pt')
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
    
