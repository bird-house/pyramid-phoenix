from pyramid.view import view_defaults
from deform import Form

from phoenix.schema import ESGFSearchSchema

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class ESGFSearch(object):
    def __init__(self, request):
        self.request = request

    def view(self):
        form = Form(schema=ESGFSearchSchema())
        return dict(form=form)
