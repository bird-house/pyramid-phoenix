from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from swiftclient import client, ClientException

from phoenix.wizard.views import Wizard
from phoenix import tdsclient 

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

class TdsBrowser(Wizard):
    def __init__(self, request):
        super(TdsBrowser, self).__init__(request, name='wizard_tdsbrowser', title="Threads browser")

    def breadcrumbs(self):
        breadcrumbs = super(TdsBrowser, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema()

    def appstruct(self):
        appstruct = super(TdsBrowser, self).appstruct()
        url = self.request.params.get('url')
        if url:
            appstruct['url'] = url
        else:
            appstruct['url'] = colander.null
        return appstruct

    def next_success(self, appstruct):
        if appstruct['url']:
            self.success(appstruct)
            return self.next('wizard_done')
        else:
            self.session.flash("Please choose dataset", queue="danger")
            return HTTPFound(location=self.request.route_path(self.name))

    def custom_view(self):
        url = self.request.params.get('url')
        if url is None:
            url = "http://www.esrl.noaa.gov/psd/thredds/catalog.xml"
        tds = tdsclient.TdsClient(url)
        items = tds.get_objects(url)
        fields = ['name', '']
    
        grid = Grid(self.request, items, fields, )
        return dict(grid=grid)

    @view_config(route_name='wizard_tdsbrowser', renderer='../templates/wizard/tdsbrowser.pt')
    def view(self):
        return super(TdsBrowser, self).view()

from webhelpers2.html.builder import HTML
from phoenix.grid import MyGrid

class Grid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(Grid, self).__init__(request, *args, **kwargs)
        self.column_formats['name'] = self.name_td
        self.column_formats[''] = self.action_td

    def name_td(self, col_num, i, item):
        name = url = content_type = None
        if hasattr(item, 'name'):
            name = item.name
            content_type = 'application/netcdf'
        else:
            name = item.title
            url = item.url
            content_type = 'application/directory'
        query = []
        query.append( ('url', url) )
        url = self.request.route_path('wizard_tdsbrowser', _query=query)
        return self.render_td(renderer="folder_element_td", url=url, name=name, content_type=content_type)

    def action_td(self, col_num, i, item):
        buttongroup = []
        return self.render_action_td(buttongroup)

    
