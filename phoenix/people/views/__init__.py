from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid


from phoenix.security import generate_access_token
from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='edit', layout='default') 
class Profile(MyView):
    def __init__(self, request):
        super(Profile, self).__init__(request, name='profile', title='')
        self.userid = self.request.matchdict.get('userid', authenticated_userid(self.request))
        self.collection = self.request.db.users

    @view_config(route_name='forget_esgf_certs', permission='submit')
    def forget_esgf_certs(self):
        user = self.collection.find_one({'identifier': self.userid})
        user['credentials'] = None
        user['cert_expires'] = None
        self.collection.update({'identifier': self.userid}, user)
        self.request.session.flash("ESGF Certficate removed.", queue='info')
        return HTTPFound(location=self.request.route_path('profile', userid=self.userid, tab='esgf'))

    @view_config(route_name='generate_twitcher_token', permission='submit')
    def generate_twitcher_token(self):
        generate_access_token(self.request.registry, self.userid)
        return HTTPFound(location=self.request.route_path('profile', userid=self.userid, tab='twitcher'))

    @view_config(route_name='profile', renderer='../templates/people/profile.pt')
    def view(self):
        tab = self.request.matchdict.get('tab', 'account')
        user = self.collection.find_one({'identifier': self.userid})
    
        lm = self.request.layout_manager
        if tab == 'twitcher':
            lm.layout.add_heading('profile_twitcher')
        elif tab == 'esgf':
            lm.layout.add_heading('profile_esgf')
        else:
            lm.layout.add_heading('profile_account')
        return dict(profile_name=user.get('name', 'Unknown'), userid=self.userid, active=tab)
