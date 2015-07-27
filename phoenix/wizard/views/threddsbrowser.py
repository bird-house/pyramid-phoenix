from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from swiftclient import client, ClientException

from phoenix.wizard.views import Wizard
import threddsclient

import logging
logger = logging.getLogger(__name__)

import colander
import deform
class Schema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = deform.widget.HiddenWidget()
        )

class ThreddsBrowser(Wizard):
    def __init__(self, request):
        super(ThreddsBrowser, self).__init__(request, name='wizard_threddsbrowser', title="Threads browser")

    def breadcrumbs(self):
        breadcrumbs = super(ThreddsBrowser, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema()

    def appstruct(self):
        appstruct = super(ThreddsBrowser, self).appstruct()
        appstruct['url'] = self.request.params.get('url', colander.null)
        return appstruct

    def next_success(self, appstruct):
        if appstruct.get('url'):
            self.success(appstruct)
            return self.next('wizard_done')
        else:
            self.session.flash("Please choose dataset", queue="danger")
            return HTTPFound(location=self.request.route_path(self.name))

    def custom_view(self):
        url = self.request.params.get('url')
        if url is None:
            url = self.wizard_state.get('wizard_threddsservice')['url']
        # TODO: back url handling needs to be changed
        back_url = None
        prev = self.request.params.get('prev')
        back_links = self.wizard_state.get('wizard_threddsservice').get('back_links', [])
        if prev:
            back_links.append(prev)
        elif len(back_links) > 0:
            back_links.pop()
        self.wizard_state.get('wizard_threddsservice')['back_links'] = back_links
        self.session.changed()
        if len(back_links) > 0:
            back_url = self.request.route_path('wizard_threddsbrowser', _query=[('url', back_links[-1])])

        logger.debug("wizard state: %s", self.wizard_state.get('wizard_threddsservice'))
        catalog = threddsclient.read_url(url)
        items = []
        items.extend( catalog.flat_references() )
        items.extend( catalog.flat_datasets() )
        fields = ['name', 'size', 'modified']
    
        grid = Grid(self.request, items, fields, )
        return dict(title=catalog.url, grid=grid, back_url=back_url)

    @view_config(route_name='wizard_threddsbrowser', renderer='../templates/wizard/threddsbrowser.pt')
    def view(self):
        return super(ThreddsBrowser, self).view()

from webhelpers2.html.builder import HTML
from phoenix.grid import MyGrid

class Grid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(Grid, self).__init__(request, *args, **kwargs)
        self.column_formats['name'] = self.name_td
        self.column_formats['size'] = self.size_td
        self.column_formats['modified'] = self.modified_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def name_td(self, col_num, i, item):
        url = None
        if item.content_type == 'application/directory':
            url = item.url
        query = []
        query.append( ('url', url) )
        query.append( ('prev', item.catalog.url) )
        url = self.request.route_path('wizard_threddsbrowser', _query=query)
        return self.render_td(renderer="folder_element_td", url=url, name=item.name, content_type=item.content_type)

    def modified_td(self, col_num, i, item):
        return self.render_timestamp_td(item.modified)

    def size_td(self, col_num, i, item):
        return self.render_size_td(item.bytes)

    def action_td(self, col_num, i, item):
        buttongroup = []
        return self.render_action_td(buttongroup)

    
