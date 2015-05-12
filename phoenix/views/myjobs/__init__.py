from pyramid.view import view_config, view_defaults

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='submit', layout='default')
class MyJobs(MyView):
    def __init__(self, request, name, title, description=None):
        super(MyJobs, self).__init__(request, name, title, description)

    def breadcrumbs(self):
        breadcrumbs = super(MyJobs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('myjobs'), title='My Jobs'))
        return breadcrumbs
