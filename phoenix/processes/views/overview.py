from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.views import MyView
from phoenix.utils import headline

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='view', layout="default")
class Overview(MyView):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='processes', title='')

    def wps_services(self):
        items = []
        for service in self.request.catalog.get_services():
            if service.group in ['admin']:
                if not self.request.has_permission('admin'):
                    continue
            elif service.group in ['admin', 'user']:
                if not self.request.has_permission('edit'):
                    continue
            url = self.request.route_path('processes_list', _query=[('wps', service.identifier)])
            items.append(dict(
                title=service.title, description=service.abstract, public=service.public, url=url))
        return items

    def pinned_processes(self):
        settings = self.request.db.settings.find_one() or {}
        processes = []
        if 'pinned_processes' in settings:
            for pinned in settings.get('pinned_processes'):
                try:
                    service_name, identifier = pinned.split('.', 1)
                    url = self.request.route_path(
                        'processes_execute', _query=[('wps', service_name), ('process', identifier)])
                    wps = WebProcessingService(
                        url=self.request.route_url('owsproxy', service_name=service_name), verify=False)
                    # TODO: need to fix owslib to handle special identifiers
                    process = wps.describeprocess(identifier)
                    description = headline(process.abstract)
                except Exception:
                    LOGGER.warn("could not add pinned process %s", pinned)
                else:
                    processes.append(dict(
                        title=process.identifier,
                        description=description,
                        url=url,
                        service_title=wps.identification.title))
        return processes

    @view_config(
        route_name='processes',
        renderer='phoenix:processes/templates/processes/overview.pt',
        accept='text/html')
    def view(self):
        return dict(title="Web Processing Services",
                    items=self.wps_services(),
                    processes=self.pinned_processes())
