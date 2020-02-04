from pyramid.view import view_config, view_defaults

from phoenix.monitor.views.list import JobList


@view_defaults(permission='view', layout='default')
class JobListJson(JobList):
    def __init__(self, request):
        JobList.__init__(self, request)

    @view_config(route_name='monitor', renderer='json', accept='application/json')
    def view(self):
        jobs_dict = JobList.view(self)
        items, count = self.filter_jobs(page=jobs_dict['page'], limit=jobs_dict['limit'], tag=jobs_dict['tag'],
                                        access=jobs_dict['access'], status=jobs_dict['status'], sort=jobs_dict['sort'])

        filtered_dict = {}
        req_props = ['access', 'status', 'page', 'limit', 'tag', 'sort',
                     'count', 'count_running', 'count_finished']
        for prop in req_props:
            if prop in jobs_dict:
                filtered_dict[prop] = jobs_dict[prop]

        filtered_dict['jobs'] = items
        return filtered_dict
