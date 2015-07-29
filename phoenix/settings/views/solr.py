from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from owslib.fes import PropertyIsEqualTo

from . import SettingsView

import logging
logger = logging.getLogger(__name__)


class SolrSettings(SettingsView):
    def __init__(self, request):
        super(SolrSettings, self).__init__(request, name='settings_solr', title='Solr')

        
    def breadcrumbs(self):
        breadcrumbs = super(SolrSettings, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    
    @view_config(route_name="clear_index")
    def index(self):
        from phoenix.tasks import clear_index
        clear_index.delay()
        self.session.flash('Cleaning Index ...', queue="info")
        return HTTPFound(location=self.request.route_path(self.name))

    
    @view_config(route_name='settings_solr', renderer='../templates/settings/solr.pt')
    def view(self):
        tasksdb = self.request.db.tasks
        csw = self.request.csw
        query = PropertyIsEqualTo('dc:format', 'THREDDS')
        csw.getrecords2(esn="full", constraints=[query], maxrecords=100)
        items = []
        for rec in csw.records.values():
            item = dict(title=rec.title, status='new')
            task = tasksdb.find_one({'url': rec.source})
            if task:
                item['status'] = task['status']
            items.append(item)
        return dict(items=items)
        


