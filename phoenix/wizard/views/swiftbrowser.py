from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from swiftclient import client, ClientException

from phoenix.wizard.views import Wizard
from phoenix import swift

import logging
logger = logging.getLogger(__name__)

import colander
from deform.widget import HiddenWidget

class Schema(colander.MappingSchema):
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

    def breadcrumbs(self):
        breadcrumbs = super(SwiftBrowser, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema()

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
        return appstruct

    def next_success(self, appstruct):
        if appstruct['container']:
            self.success(appstruct)
            return self.next('wizard_done')
        else:
            self.session.flash("Please choose container", queue="danger")
            return HTTPFound(location=self.request.route_path(self.name))

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
        # TODO: filter with choosen mime type
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

    @view_config(route_name='wizard_swiftbrowser', renderer='../templates/wizard/swiftbrowser.pt')
    def view(self):
        return super(SwiftBrowser, self).view()

from webhelpers2.html.builder import HTML
from phoenix.grid import MyGrid

class SwiftBrowserGrid(MyGrid):
    def __init__(self, request, container, *args, **kwargs):
        super(SwiftBrowserGrid, self).__init__(request, *args, **kwargs)
        self.container = container
        self.column_formats['name'] = self.name_td
        self.column_formats['created'] = self.timestamp_td('last_modified')
        self.column_formats['objects'] = self.label_td('count')
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
        url = self.request.route_path('wizard_swiftbrowser', _query=query)
        return self.render_td(renderer="folder_element_td", url=url, name=name, content_type=content_type)

    def size_td(self, col_num, i, item):
        size = None
        if not item.has_key('subdir'):
            size = item.get('bytes')
        return self.render_size_td(size)

    def action_td(self, col_num, i, item):
        buttongroup = []
        return self.render_action_td(buttongroup)

    
