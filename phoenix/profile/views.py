from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from deform import Form, ValidationFailure

from phoenix.security import generate_access_token
from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default') 
class Profile(MyView):
    def __init__(self, request):
        super(Profile, self).__init__(request, name='profile', title='')

    @view_config(route_name='forget_esgf_certs', permission='submit')
    def forget_esgf_certs(self):
        userid = authenticated_userid(self.request)
        user = self.request.db.users.find_one({'identifier':userid})
        user['credentials'] = None
        user['cert_expires'] = None
        self.request.db.users.update({'identifier':userid}, user)
        self.request.session.flash("ESGF Certficate removed.", queue='info')
        return HTTPFound(location=self.request.route_path('profile', tab='esgf'))

    @view_config(route_name='generate_twitcher_token', permission='submit')
    def generate_twitcher_token(self):
        generate_access_token(self.request, authenticated_userid(self.request))
        return HTTPFound(location=self.request.route_path('profile', tab='twitcher'))

    @view_config(route_name='profile', renderer='templates/profile/profile.pt')
    def view(self):
        tab = self.request.matchdict.get('tab', 'account')
    
        lm = self.request.layout_manager
        if tab == 'account':
            lm.layout.add_heading('profile_account')
        elif tab == 'twitcher':
            lm.layout.add_heading('profile_twitcher')
        elif tab == 'esgf':
            lm.layout.add_heading('profile_esgf')
        elif tab == 'swift':
            lm.layout.add_heading('profile_swift')
        return dict(active=tab)

    
