from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

import colander
@colander.deferred
def deferred_esgf_files_widget(node, kw):
    import json
    selection = kw.get('selection', {})
    search = json.loads(selection)
    from phoenix.widget import EsgFilesWidget
    return EsgFilesWidget(url="/esg-search", search_type='File', search=search)

class ESGFFilesSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_esgf_files_widget(node, kw):
        import json
        selection = kw.get('selection', {})
        search = json.loads(selection)
        from phoenix.widget import EsgFilesWidget
        return EsgFilesWidget(url="/esg-search", search_type='File', search=search)
    
    url = colander.SchemaNode(
        colander.Set(),
        widget = deferred_esgf_files_widget)

class ESGFFileSearch(Wizard):
    def __init__(self, request):
        super(ESGFFileSearch, self).__init__(
            request, name='wizard_esgf_files',
            title="ESGF File Search")

    def schema(self):
        #from phoenix.schema import NoSchema
        #return NoSchema()
        return ESGFFilesSchema().bind(selection=self.wizard_state.get('wizard_esgf')['selection'])

    def cert_ok(self):
        # TODO: this is the wrong place to skip steps
        cert_expires = self.get_user().get('cert_expires')
        if cert_expires != None:
            logger.debug('cert_expires: %s', cert_expires)
            from phoenix.utils import localize_datetime
            from dateutil import parser as datetime_parser
            timestamp = datetime_parser.parse(cert_expires)
            logger.debug("timezone: %s", timestamp.tzname())
            import datetime
            now = localize_datetime(datetime.datetime.utcnow())
            valid_hours = datetime.timedelta(hours=8)
            # cert must be valid for some hours
            if timestamp > now + valid_hours:
                return True
        return False

    def next_success(self, appstruct):
        self.success(appstruct)
        
        if self.cert_ok():
            return self.next('wizard_check_parameters')
        return self.next('wizard_esgf_credentials')

    def query_esgf_files(self):
        selection = self.wizard_state.get('wizard_esgf')['selection']

        import json
        search = json.loads(selection)
        constraints = {}
        for facet in search.get('facets', '').split(','):
            key,value = facet.split(':')
            constraints[key] = value
        constraints['start'] = search.get('start')
        constraints['end'] = search.get('end')
        constraints['bbox'] = search.get('bbox')

        from phoenix.models import query_esgf_files
        result_ds = query_esgf_files(
            latest=search.get('latest'), 
            replica=search.get('replica'),
            distrib=search.get('distrib'),
            **constraints)
        result = []
        for ds in result_ds:
            abstract = 'size = %d MB, number of files = %d' % (ds.get('size')/1024.0/1024.0, ds.get('number_of_files'))
            result.append(dict(identifier=ds.get('id'), title=ds.get('title'), abstract=abstract, subjects=[]))
        return result

    def custom_view_disabled(self):
        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        #items = self.search_csw(query)
        items = self.query_esgf_files()
        for item in items:
            # TODO: refactor this
            if item['identifier'] in self.appstruct().get('selection', []):
                item['selected'] = True
            else:
                item['selected'] = False

        grid = ESGFFileSearchGrid(
                self.request,
                items,
                ['title', 'selected'],
            )
        return dict(grid=grid, items=items)
        
    @view_config(route_name='wizard_esgf_files', renderer='phoenix:templates/wizard/esgffiles.pt')
    def view(self):
        return super(ESGFFileSearch, self).view()


from phoenix.grid import MyGrid

class ESGFFileSearchGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ESGFFileSearchGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['selected'] = self.selected_td
        self.column_formats['title'] = self.title_td

    def title_td(self, col_num, i, item):
        return self.render_title_td(item['title'], item['abstract'], item.get('subjects'))

    def selected_td(self, col_num, i, item):
        from string import Template
        from webhelpers.html.builder import HTML

        icon_class = "glyphicon glyphicon-thumbs-down"
        if item.get('selected') == True:
            icon_class = "glyphicon glyphicon-thumbs-up"
        div = Template("""\
        <a class="select" data-value="${recordid}" href="#"><i class="${icon_class}"></i></a>
        """)
        return HTML.td(HTML.literal(div.substitute({'recordid': item['identifier'],
                                                    'icon_class': icon_class} )))
