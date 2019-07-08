from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.views import MyView
from phoenix.utils import wps_caps_url


def get_process_media(process):
    for metadata in process.metadata:
        if metadata.role == 'http://www.opengis.net/spec/wps/2.0/def/process/description/media':
            return metadata.url
    return None


@view_defaults(permission='view', layout="default")
class ProcessList(MyView):
    def __init__(self, request):
        self.service_name = request.params.get('wps')
        self.wps = WebProcessingService(
            url=request.route_url('owsproxy', service_name=self.service_name),
            verify=False)
        super(ProcessList, self).__init__(request, name='processes_list', title='')

    @view_config(
        route_name='processes_list',
        renderer='phoenix:processes/templates/processes/list.pt',
        accept='text/html')
    def view(self):
        items = []
        for process in self.wps.processes:
            item = dict(
                title=process.title,
                version=process.processVersion,
                description=getattr(process, 'abstract', ''),
                media=get_process_media(process),
                url=self.request.route_path('processes_execute',
                                            _query=[('wps', self.service_name), ('process', process.identifier)]))
            items.append(item)
        return dict(
            url=wps_caps_url(self.wps.url),
            title=self.wps.identification.title,
            description=self.wps.identification.abstract,
            provider_name=self.wps.provider.name,
            provider_site=self.wps.provider.url,
            items=items)
