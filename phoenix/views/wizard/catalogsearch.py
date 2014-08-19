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

import logging
logger = logging.getLogger(__name__)

class CatalogSearch(Wizard):
    def __init__(self, request):
        super(CatalogSearch, self).__init__(
            request,
            "CSW Catalog Search")
        self.description = self.wizard_state.get('complex_input_identifier')

    def schema(self):
        from phoenix.schema import CatalogSearchSchema
        return CatalogSearchSchema()

    def success(self, appstruct):
        #self.wizard_state.set('esgf_files', appstruct.get('url'))
        pass

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_check_parameters')

    def search_csw(self, query=''):
        keywords = [k for k in map(str.strip, str(query).split(' ')) if len(k)>0]

        # TODO: search all formats
        format = self.wizard_state.get('mime_types')[0]

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
        
    @view_config(renderer='json', name='select.csw')
    def select_csw(self):
        # TODO: refactor this ... not efficient
        identifier = self.request.params.get('identifier', None)
        logger.debug('called with %s', identifier)
        if identifier is not None:
            selection = self.wizard_state.get('csw_selection', [])
            if identifier in selection:
                selection.remove(identifier)
            else:
                selection.append(identifier)
            self.wizard_state.set('csw_selection', selection)
        return {}

    def appstruct(self):
        return dict(csw_selection=self.wizard_state.get('csw_selection'))

    def custom_view(self):
        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        items = self.search_csw(query)
        for item in items:            
            if item['identifier'] in self.wizard_state.get('csw_selection', []):
                item['selected'] = True
            else:
                item['selected'] = False

        grid = CatalogSearchGrid(
                self.request,
                items,
                ['title', 'format', 'selected'],
            )
        return dict(grid=grid, items=items)

    def breadcrumbs(self):
        breadcrumbs = super(CatalogSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_csw', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_csw', renderer='phoenix:templates/wizard/csw.pt')
    def view(self):
        return super(CatalogSearch, self).view()

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

    
