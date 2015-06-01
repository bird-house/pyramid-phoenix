from pyramid.view import view_config

from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)

import colander
class CatalogSearchSchema(colander.MappingSchema):
    pass

class CatalogSearch(Wizard):
    def __init__(self, request):
        super(CatalogSearch, self).__init__(
            request, name='wizard_csw', title="CSW Catalog Search")
        self.description = self.wizard_state.get('wizard_complex_inputs')['identifier']

    def schema(self):
        return CatalogSearchSchema()

    def next_success(self, appstruct):
        #self.success(appstruct)
        return self.next('wizard_done')

    def search_csw(self, query=''):
        keywords = [k for k in map(str.strip, str(query).split(' ')) if len(k)>0]

        # TODO: search all formats
        format = self.wizard_state.get('wizard_complex_inputs')['mime_types'][0]

        from string import Template
        cql_tmpl = Template("""\
        dc:creator='${email}'\
        and dc:format='${format}'
        """)
        cql = cql_tmpl.substitute({
            'email': self.get_user().get('email'),
            'format': format})
        cql_keyword_tmpl = Template('and csw:AnyText like "%${keyword}%"')
        for keyword in keywords:
            cql += cql_keyword_tmpl.substitute({'keyword': keyword})

        results = []
        try:
            self.csw.getrecords(esn="full", cql=cql)
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    source = myrec.source,
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
                    references = myrec.references,
                    ))
        except:
            logger.exception('could not get items for csw.')
        return results
        
    @view_config(route_name='wizard_csw_select', renderer='json')
    def select_record(self):
        recordid = self.request.matchdict.get('recordid')
        # TODO: refactor this ... not efficient
        appstruct = self.appstruct()
        if recordid is not None:
            selection = appstruct.get('selection', [])
            if recordid in selection:
                selection.remove(recordid)
            else:
                selection.append(recordid)
            appstruct['selection'] = selection
            self.success(appstruct)
        return {}

    def custom_view(self):
        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        items = self.search_csw(query)
        for item in items:
            # TODO: refactor this
            if item['identifier'] in self.appstruct().get('selection', []):
                item['selected'] = True
            else:
                item['selected'] = False

        grid = CatalogSearchGrid(
                self.request,
                items,
                ['title', 'format', 'selected'],
            )
        return dict(grid=grid, items=items)

    @view_config(route_name='wizard_csw', renderer='phoenix:templates/wizard/csw.pt')
    def view(self):
        return super(CatalogSearch, self).view()

from phoenix.grid import MyGrid

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
        if item.get('selected') == True:
            icon_class = "glyphicon glyphicon-thumbs-up"
        div = Template("""\
        <a class="select" data-value="${recordid}" href="#"><i class="${icon_class}"></i></a>
        """)
        return HTML.td(HTML.literal(div.substitute({'recordid': item['identifier'],
                                                    'icon_class': icon_class} )))


    
