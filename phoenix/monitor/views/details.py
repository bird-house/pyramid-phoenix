from pyramid.view import view_config, view_defaults

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class Details(MyView):
    def __init__(self, request):
        super(Details, self).__init__(
            request, name='monitor_details', title='Details')

    def breadcrumbs(self):
        breadcrumbs = super(Details, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('monitor'), title='Monitor'))
        breadcrumbs.append(dict(route_path='', title=self.title))
        return breadcrumbs

    @view_config(route_name='monitor_details', renderer='../templates/monitor/details.pt')
    def view(self):
        tab = self.request.matchdict.get('tab')
        # TODO: this is a bit fishy ...
        job_id = self.request.matchdict.get('job_id')
        if job_id is not None:
            self.session['job_id'] = job_id
            self.session.changed()

        lm = self.request.layout_manager
        if tab == 'outputs':
            lm.layout.add_heading('monitor_outputs')
        elif tab == 'inputs':
            lm.layout.add_heading('monitor_inputs')
        else:
            lm.layout.add_heading('monitor_log')

        return dict(active=tab, job_id=job_id)
