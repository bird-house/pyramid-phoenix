from pyramid.view import view_config

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class Services(SettingsView):
    def __init__(self, request):
        super(Services, self).__init__(
            request, name='services', title='Services')
        self.csw = self.request.csw

    def breadcrumbs(self):
        breadcrumbs = super(Services, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
        
    @view_config(route_name='remove_service')
    def remove(self):
        try:
            service_id = self.request.matchdict.get('service_id')
            self.csw.transaction(ttype='delete', typename='csw:Record', identifier=service_id )
            self.session.flash('Removed Service %s.' % service_id, queue="info")
        except Exception,e:
            msg = "Could not remove service %s" % e
            logger.exception(msg)
            self.session.flash(msg, queue="danger")
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name="services", renderer='../templates/services/service_list.pt')
    def view(self):
        self.csw.getrecords2(esn="full", maxrecords=100)
            
        grid = Grid(
                self.request,
                self.csw.records.values(),
                ['title', 'type', ''],
            )
        return dict(grid=grid)

from phoenix.grid import MyGrid
class Grid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(Grid, self).__init__(request, *args, **kwargs)
        self.column_formats[''] = self.action_td
        self.column_formats['title'] = self.title_td
        self.column_formats['type'] = self.type_td
        self.exclude_ordering = self.columns

    def title_td(self, col_num, i, item):
        return self.render_title_td(item.title, item.abstract, item.subjects)

    def type_td(self, col_num, i, item):
        return self.render_format_td(item.format, item.source)

    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append(
            ("remove", item.identifier, "glyphicon glyphicon-trash text-danger", "",
            self.request.route_path('remove_service', service_id=item.identifier),
            False) )
        return self.render_action_td(buttongroup)
       
