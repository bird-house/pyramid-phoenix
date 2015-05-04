from pyramid.view import view_config

from swiftclient import client, ClientException

from phoenix.views.wizard import Wizard
from phoenix.models import swift

import logging
logger = logging.getLogger(__name__)

import colander
from deform.widget import HiddenWidget
class SwiftBrowserSchema(colander.MappingSchema):
    container = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = HiddenWidget()
        )
    prefix = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = HiddenWidget()
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

    def appstruct(self):
        appstruct = super(SwiftBrowser, self).appstruct()
        container = self.request.params.get('container')
        if container:
            appstruct['container'] = container
        else:
            appstruct['container'] = colander.null
        prefix = self.request.params.get('prefix')
        if prefix:
            appstruct['prefix'] = prefix
        else:
            appstruct['prefix'] = colander.null
        logger.debug("appstruct = %s", appstruct)
        return appstruct

    def next_success(self, appstruct):
        if appstruct['container'] and appstruct['prefix']:
            self.success(appstruct)
            return self.next('wizard_done')
        else:
            return self.flash_error("Please choose container and prefix.")

    def custom_view(self):
        container = self.request.params.get('container')
        prefix = self.request.params.get('prefix')
        items = fields = []
        if container:
            items = swift.get_objects(self.storage_url, self.auth_token, container, prefix=prefix)
            fields = ['name', 'created', 'size', '']
        else:
            items = swift.get_containers(self.storage_url, self.auth_token)
            fields = ['name', 'objects', 'size', '']
        filtered_items = []
        for item in items:
            logger.debug(item)
            if item.has_key('subdir'):
                # always show directories
                filtered_items.append(item)
            elif item['name'].startswith('.'):
                # don't show hidden files
                continue
            elif item.has_key('count'):
                # always show container
                filtered_items.append(item)
            elif item['content_type'] in ['application/directory', 'application/x-directory']:
                # always show directories
                filtered_items.append(item)
            elif item['content_type'] in ['application/x-netcdf']:
                # show only netcdf files
                filtered_items.append(item)

        grid = SwiftBrowserGrid(
            self.request,
            container,
            filtered_items,
            fields,
            )
        return dict(grid=grid, items=items, container=container, prefixes=swift.prefix_list(prefix))

    @view_config(route_name='wizard_swiftbrowser', renderer='phoenix:templates/wizard/swiftbrowser.pt')
    def view(self):
        return super(SwiftBrowser, self).view()

from webhelpers2.html.builder import HTML
from phoenix.grid import MyGrid

class SwiftBrowserGrid(MyGrid):
    def __init__(self, request, container, *args, **kwargs):
        super(SwiftBrowserGrid, self).__init__(request, *args, **kwargs)
        self.container = container
        self.column_formats['name'] = self.name_td
        self.column_formats['created'] = self.created_td
        self.column_formats['objects'] = self.objects_td
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

    def objects_td(self, col_num, i, item):
        return self.render_label_td(item.get('count') )

    def size_td(self, col_num, i, item):
        from webhelpers2.number import format_byte_size
        size = ''
        if not item.has_key('subdir'):
            size = format_byte_size( item.get('bytes') )
        return self.render_label_td(size)

    def action_td(self, col_num, i, item):
        buttongroup = []
        return self.render_action_td(buttongroup)

    
