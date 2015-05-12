from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, ValidationFailure

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default') 
class Profile(MyView):
    def __init__(self, request):
        super(Profile, self).__init__(request, name='profile', title='Profile')
        self.description = "Update your profile details."

    @view_config(route_name='profile', renderer='phoenix:templates/profile.pt')
    def view(self):
        tab = self.request.matchdict.get('tab', 'profile')
    
        lm = self.request.layout_manager
        if tab == 'profile':
            lm.layout.add_heading('profile_account')
        elif tab == 'esgf':
            lm.layout.add_heading('profile_esgf')
        elif tab == 'swift':
            lm.layout.add_heading('profile_swift')
        return dict(active=tab)
