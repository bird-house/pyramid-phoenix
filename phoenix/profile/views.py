from datetime import datetime

from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from deform import Form, ValidationFailure

from phoenix.views import MyView

from twitcher.tokens import tokengenerator_factory
from twitcher.tokens import tokenstore_factory

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default') 
class Profile(MyView):
    def __init__(self, request):
        super(Profile, self).__init__(request, name='profile', title='')

    @view_config(route_name='forget_esgf_certs')
    def forget_esgf_certs(self):
        userid = authenticated_userid(self.request)
        user = self.request.db.users.find_one({'identifier':userid})
        user['credentials'] = None
        user['cert_expires'] = None
        self.request.db.users.update({'identifier':userid}, user)
        self.request.session.flash("ESGF Certficate removed.", queue='info')
        return HTTPFound(location=self.request.route_path('profile', tab='esgf'))

    @view_config(route_name='generate_twitcher_token')
    def generate_twitcher_token(self):
        userid = authenticated_userid(self.request)
        user = self.request.db.users.find_one({'identifier':userid})

        tokengenerator = tokengenerator_factory(self.request.registry)
        tokenstore = tokenstore_factory(self.request.registry)
        access_token = tokengenerator.create_access_token(valid_in_hours=1, user_environ={})
        tokenstore.save_token(access_token)
        
        user['twitcher_token'] = access_token['token']
        user['twitcher_token_expires'] = datetime.utcfromtimestamp(int(access_token['expires_at'])).strftime(format="%Y-%m-%d %H:%M:%S UTC")
        self.request.db.users.update({'identifier':userid}, user)
        self.request.session.flash("Twitcher access token generated.", queue='info')
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

    
