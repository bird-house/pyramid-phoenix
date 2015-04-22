from pyramid.view import view_config

from swiftclient import client, ClientException

from phoenix.views.wizard import Wizard
from phoenix.models import get_containers, get_objects, prefix_list

import logging
logger = logging.getLogger(__name__)

import colander
class SwiftBrowserSchema(colander.MappingSchema):
    container = colander.SchemaNode(
        colander.String()
        )
    prefix = colander.SchemaNode(
        colander.String()
        )

class SwiftBrowser(Wizard):
    def __init__(self, request):
        super(SwiftBrowser, self).__init__(
            request, name='wizard_swiftbrowser', title="Swiftbrowser")
        self.description = None
        user = self.get_user()
        self.storage_url = user.get('swift_storage_url')
        self.auth_token = user.get('swift_auth_token')

    def schema(self):
        return SwiftBrowserSchema()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    def custom_view(self):
        container = self.request.params.get('container')
        prefix = self.request.params.get('prefix')
        items = []
        if container is None:
            items = get_containers(self.storage_url, self.auth_token)
        else:
            items = get_objects(self.storage_url, self.auth_token, container, prefix=prefix)
        grid = SwiftBrowserGrid(
            self.request,
            container,
            items,
            ['name', 'created', 'size', ''],
            )
        return dict(grid=grid, items=items, container=container, prefixes=prefix_list(prefix))

    @view_config(route_name='wizard_swiftbrowser', renderer='phoenix:templates/wizard/swiftbrowser.pt')
    def view(self):
        return super(SwiftBrowser, self).view()

from webhelpers.html.builder import HTML
from phoenix.grid import MyGrid

class SwiftBrowserGrid(MyGrid):
    def __init__(self, request, container, *args, **kwargs):
        super(SwiftBrowserGrid, self).__init__(request, *args, **kwargs)
        self.container = container
        self.column_formats['name'] = self.name_td
        self.column_formats['created'] = self.created_td
        self.column_formats['size'] = self.size_td
        self.column_formats[''] = self.action_td

    def name_td(self, col_num, i, item):
        prefix = content_type = None
        if item.has_key('subdir'):
            prefix = item['subdir']
            content_type = 'application/directory'
        else:
            prefix = item['name']
            content_type = item.get('content_type', 'application/directory')
        query = []
        if self.container is None:
            query.append( ('container', prefix))
        else:
            query.append( ('container', self.container))
            query.append( ('prefix', prefix) )
        name = prefix.strip('/')
        name = name.split('/')[-1]
        url = self.request.route_url('wizard_swiftbrowser', _query=query)
        return self.render_td(renderer="folder_element_td", url=url, name=name, content_type=content_type)

    def created_td(self, col_num, i, item):
        return self.render_timestamp_td(item.get('last_modified'))

    def size_td(self, col_num, i, item):
        from phoenix.utils import filesizeformat
        return self.render_title_td(filesizeformat( item.get('bytes') ))

    def action_td(self, col_num, i, item):
        buttongroup = []
    ##     buttongroup.append( ("show", item.get('identifier'), "icon-th-list", "Show", 
    ##                          self.request.route_url('process_outputs', tab='outputs', jobid=item.get('identifier')), False) )
    ##     buttongroup.append( ("remove", item.get('identifier'), "icon-trash", "Remove", 
    ##                          self.request.route_url('remove_myjob', jobid=item.get('identifier')), False) )
        return self.render_action_td(buttongroup)

    
