from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from owslib.fes import PropertyIsEqualTo

from . import SettingsView

import logging
logger = logging.getLogger(__name__)


class SolrSettings(SettingsView):
    def __init__(self, request):
        super(SolrSettings, self).__init__(request, name='settings_solr', title='Solr')
        self.csw = self.request.csw
        self.tasksdb = self.request.db.tasks

        
    def breadcrumbs(self):
        breadcrumbs = super(SolrSettings, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    
    @view_config(route_name="index_service")
    def index_service(self):
        service_id = self.request.matchdict.get('service_id')
        self.csw.getrecordbyid(id=[service_id])
        service = self.csw.records[service_id]
        from phoenix.tasks import index_thredds
        index_thredds.delay(url=service.source)
        self.session.flash('Start Indexing of Service %s.' % service.title, queue="info")
        return HTTPFound(location=self.request.route_path(self.name))

    
    @view_config(route_name="clear_index")
    def clear_index(self):
        from phoenix.tasks import clear_index
        clear_index.delay()
        self.session.flash('Cleaning Index ...', queue="info")
        return HTTPFound(location=self.request.route_path(self.name))

    
    @view_config(route_name='settings_solr', renderer='../templates/settings/solr.pt')
    def view(self):
        query = PropertyIsEqualTo('dc:format', 'THREDDS')
        self.csw.getrecords2(esn="full", constraints=[query], maxrecords=100)
        items = []
        for rec in self.csw.records.values():
            item = dict(title=rec.title, status='new', service_id=rec.identifier)
            task = self.tasksdb.find_one({'url': rec.source})
            if task:
                item['status'] = task['status']
            items.append(item)
        return dict(items=items)
        


