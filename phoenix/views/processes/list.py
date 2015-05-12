from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService
from owslib.util import build_get_url

from phoenix.views.processes import Processes
from phoenix.grid import MyGrid
from phoenix import models
import deform

import logging
logger = logging.getLogger(__name__)

class ProcessList(Processes):
    def __init__(self, request):
        self.wps = WebProcessingService(url=request.params.get('url'))
        title = self.wps.identification.title
        super(ProcessList, self).__init__(request, name='processes_list',
                                          title=title,
                                          description="Choose a process to execute.")

    def breadcrumbs(self):
        breadcrumbs = super(ProcessList, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='processes_list', renderer='phoenix:templates/processes/list.pt')
    def view(self):
        items = self.wps.processes

        grid = ProcessGrid(
                self.request,
                self.wps,
                items,
                ['Process', '']
            )

        return dict(
            url=self.wps.url,
            description=self.wps.identification.abstract,
            version=self.wps.version,
            provider_name=self.wps.provider.name,
            provider_site=self.wps.provider.url,
            grid=grid,
            items=items)

class ProcessGrid(MyGrid):
    def __init__(self, request, wps, *args, **kwargs):
        super(ProcessGrid, self).__init__(request, *args, **kwargs)
        self.wps = wps
        self.labels['Process'] = ''
        self.column_formats['Process'] = self.title_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def title_td(self, col_num, i, item):
        query = dict(service='wps', version='1.0.0', request='describeprocess', identifier=item.identifier)
        return self.render_title_td(
            title="%s %s" % (item.title, item.processVersion), 
            abstract=getattr(item, 'abstract', ''),
            format='XML',
            source=build_get_url(self.wps.url, query))

    def action_td(self, col_num, i, item):
        query = [('url', self.wps.url), ('identifier', item.identifier)]
        route_path = self.request.route_path('processes_execute', _query=query)
        logger.debug('route path = %s', route_path)
        
        buttongroup = []
        buttongroup.append( ("execute", "", "glyphicon glyphicon-cog", "Execute Process", 
                             route_path, False) )
        return self.render_action_td(buttongroup)
    
