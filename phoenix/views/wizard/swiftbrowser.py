from pyramid.view import view_config

from swiftclient import client, ClientException

from phoenix.views.wizard import Wizard
from phoenix.models import get_folders, get_containers

import logging
logger = logging.getLogger(__name__)

class SwiftBrowser(Wizard):
    def __init__(self, request):
        super(SwiftBrowser, self).__init__(
            request, name='wizard_swiftbrowser', title="Swiftbrowser")
        self.description = None
        user = self.get_user()
        self.storage_url = user.get('swift_storage_url')
        self.auth_token = user.get('swift_auth_token')

    def schema(self):
        from phoenix.schema import SwiftBrowserSchema
        user = self.get_user()
        storage_url = user.get('swift_storage_url')
        auth_token = user.get('swift_auth_token')
            
        return SwiftBrowserSchema().bind(containers=get_folders(storage_url, auth_token))

    def next_success(self, appstruct):
        self.success(appstruct)
        container = appstruct['container']
        parts = container.split('/')
        container = parts[0]
        value = dict(container=container)
        if len(parts) > 1:
            prefix = '/'.join(parts[1:])
            value['prefix'] = prefix
        return self.next('wizard_done')
    
    @view_config(route_name='wizard_swiftbrowser', renderer='phoenix:templates/wizard/swiftbrowser.pt')
    def view(self):
        #return super(SwiftBrowser, self).view()
        container = self.request.params.get('container')
        prefix = self.request.params.get('prefix')
        element = self.request.params.get('element')
        logger.debug('container=%s, prefix=%s, element=%s', container, prefix, element)
        if container is None:
            container = element
        else:
            prefix = element
        
        items = []
        if container is None:
            items = get_containers(self.storage_url, self.auth_token)
        else:
            headers, items = client.get_container(self.storage_url, self.auth_token, container, delimiter="/", prefix=prefix)
        grid = SwiftBrowserGrid(
            self.request,
            container,
            prefix,
            items,
            ['name', 'created', 'size', ''],
            )
        return dict(grid=grid, items=items)


from string import Template
from webhelpers.html.builder import HTML
from phoenix.grid import MyGrid

class SwiftBrowserGrid(MyGrid):
    def __init__(self, request, container, prefix, *args, **kwargs):
        super(SwiftBrowserGrid, self).__init__(request, *args, **kwargs)
        self.container = container
        self.prefix = prefix
        self.column_formats['name'] = self.name_td
        self.column_formats['created'] = self.created_td
        self.column_formats['size'] = self.size_td
        self.column_formats[''] = self.action_td

    def name_td(self, col_num, i, item):
        name = content_type = None
        if item.has_key('subdir'):
            name = item['subdir']
            content_type = 'application/directory'
        else:
            name = item['name']
            content_type = item.get('content_type', 'application/directory')
        url = self.request.route_url('wizard_swiftbrowser')
        url = url + '?'
        if self.container is not None:
            url = url + "container=%s" % self.container
            if self.prefix is not None:
                url = url + "&prefix=%s" % self.prefix
        url = url + "&element="
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

    
