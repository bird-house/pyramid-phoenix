from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from phoenix.tasks.solr import clear_index
from phoenix.tasks.solr import index_thredds
from phoenix.settings import load_settings
from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='admin', layout='default')
class SolrSettings(MyView):
    def __init__(self, request):
        super(SolrSettings, self).__init__(request, name='settings_solr', title='Solr')

    def breadcrumbs(self):
        breadcrumbs = super(SolrSettings, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings'), title="Settings"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name, tab="index"), title=self.title))
        return breadcrumbs

    @view_config(route_name="index_service")
    def index_service(self):
        service_id = self.request.matchdict.get('service_id')
        service = self.request.catalog.get_record_by_id(service_id)
        settings = load_settings(self.request)
        index_thredds.delay(url=service.source,
                            maxrecords=settings.get('solr_maxrecords'),
                            depth=settings.get('solr_depth'))
        self.session.flash('Start Indexing of Service %s. Reload page to see status ...' % service.title,
                           queue="danger")
        return HTTPFound(location=self.request.route_path(self.name, tab="index"))

    @view_config(route_name="clear_index")
    def clear_index(self):
        clear_index.delay()
        self.session.flash('Cleaning Index ... Reload page to see status ...', queue="danger")
        return HTTPFound(location=self.request.route_path(self.name, tab="index"))

    @view_config(route_name='settings_solr', renderer='../templates/settings/solr.pt')
    def view(self):
        tab = self.request.matchdict.get('tab', 'params')

        lm = self.request.layout_manager
        if tab == 'params':
            lm.layout.add_heading('solr_params')
        elif tab == 'index':
            lm.layout.add_heading('solr_index')
        return dict(active=tab)
