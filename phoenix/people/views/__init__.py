from pyramid.view import view_config, view_defaults
from pyramid.security import authenticated_userid

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='edit', layout='default') 
class Profile(MyView):
    def __init__(self, request):
        super(Profile, self).__init__(request, name='profile', title='')
        self.collection = self.request.db.users

    @view_config(route_name='profile', renderer='../templates/people/profile.pt')
    def view(self):
        userid = self.request.matchdict.get('userid', authenticated_userid(self.request))
        tab = self.request.matchdict.get('tab', 'account')
        user = self.collection.find_one({'identifier': userid})
    
        lm = self.request.layout_manager
        if tab == 'twitcher':
            lm.layout.add_heading('profile_twitcher')
        elif tab == 'esgf':
            lm.layout.add_heading('profile_esgf')
        else:
            lm.layout.add_heading('profile_account')
        return dict(profile_name=user.get('name', 'Unknown'), userid=userid, active=tab)
