from deform import Form
from pyramid.view import view_defaults

from phoenix.esgf.schema import ESGFSearchSchema
from phoenix.esgf.search import ESGFSearch


@view_defaults(permission='view', layout='default')
class ESGFSearchActions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.esgfsearch = ESGFSearch(request)

    def search_datasets(self):
        if self.request.has_permission('edit'):
            if not self.request.cert_ok:
                msg = 'You are not allowed to access ESGF data. Please <a href="{}">update</a> your ESGF credentials.'
                callback = self.request.route_path('esgfsearch')
                self.session.flash(
                    msg.format(self.request.route_path('esgflogon', _query=[('callback', callback)])),
                    queue='danger')
        result = dict()
        result.update(self.esgfsearch.query_params())
        result.update(self.esgfsearch.search_datasets())
        result['form'] = Form(ESGFSearchSchema())
        result['quickview'] = True
        return result

    def search_items(self):
        return self.esgfsearch.search_items()
