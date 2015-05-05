from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, ValidationFailure

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default') 
class MyAccount(MyView):
    def __init__(self, request):
        super(MyAccount, self).__init__(request, name='myaccount', title='My Account')
        self.description = "Update your profile details."

    @view_config(route_name='myaccount', renderer='phoenix:templates/myaccount.pt')
    def view(self):
        tab = self.request.matchdict.get('tab', 'profile')
    
        lm = self.request.layout_manager
        if tab == 'profile':
            lm.layout.add_heading('myaccount_profile')
        elif tab == 'esgf':
            lm.layout.add_heading('myaccount_esgf')
        elif tab == 'swift':
            lm.layout.add_heading('myaccount_swift')
        return dict(active=tab)
