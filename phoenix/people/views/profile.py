from datetime import datetime

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from deform import Form, ValidationFailure, Button

from phoenix.views import MyView
from phoenix.utils import ActionButton
from phoenix.people.schema import (
    ProfileSchema,
    TokenSchema,
    GroupSchema
)
from phoenix.security import check_csrf_token

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='edit', layout='default')
class Profile(MyView):
    def __init__(self, request):
        super(Profile, self).__init__(request, name='profile', title='')
        self.userid = self.request.matchdict.get('userid', authenticated_userid(self.request))
        self.tab = self.request.matchdict.get('tab', 'account')
        self.collection = self.request.db.users
        self.user = self.collection.find_one({'identifier': self.userid})

    def panel_title(self):
        if self.tab == 'token':
            title = "Personal access token"
        elif self.tab == 'group':
            title = 'Group permission'
        else:
            title = 'Profile'
        return title

    def appstruct(self):
        appstruct = self.collection.find_one({'identifier': self.userid})
        token = self.user.get('token')
        if token:
            appstruct['token'] = token['access_token']
            expires_at = datetime.utcfromtimestamp(
                int(token.get('expires_at'))).strftime(format="%Y-%m-%d %H:%M:%S UTC")
            appstruct['token_expires_at'] = expires_at
        return appstruct

    def readonly(self):
        if self.tab == 'group':
            return not self.request.has_permission('admin')
        else:
            return False

    def schema(self):
        if self.tab == 'token':
            schema = TokenSchema()
        elif self.tab == 'group':
            schema = GroupSchema()
        else:
            schema = ProfileSchema()
        return schema.bind(request=self.request)

    def generate_form(self):
        if self.tab == 'group':
            btn = Button(name='update', title='Update Group Permission',
                         css_class="btn btn-success btn-lg btn-block",
                         disabled=not self.request.has_permission('admin'))
            form = Form(schema=self.schema(), buttons=(btn,),
                        formid='deform')
        elif self.tab == 'profile':
            btn = Button(name='update', title='Update Profile', css_class="btn btn-success btn-lg btn-block")
            form = Form(schema=self.schema(), buttons=(btn,), formid='deform')
        else:
            form = Form(schema=self.schema(), formid='deform')
        return form

    def generate_buttons(self):
        btns = []
        if self.tab == 'token':
            btn = ActionButton(name='refresh_token', title='Refresh Token',
                               css_class="btn btn-success btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href=self.request.route_path('refresh_token'))
            btns.append(btn)
        return btns

    def process_form(self, form):
        try:
            controls = list(self.request.POST.items())
            appstruct = form.validate(controls)
            for key in ['name', 'email', 'organisation', 'notes', 'group']:
                if key in appstruct:
                    self.user[key] = appstruct.get(key)
            self.collection.update({'identifier': self.userid}, self.user)
        except ValidationFailure as e:
            LOGGER.exception('validation of form failed.')
            return dict(form=e.render())
        else:
            self.request.session.flash("Your profile was updated.", queue='success')
        return HTTPFound(location=self.request.current_route_path())

    @view_config(route_name='profile', renderer='phoenix:people/templates/people/profile.pt')
    def view(self):
        if self.request.registry.settings.get("phoenix.local_user_management", "true").lower() != "true":
            return HTTPNotFound()
        form = self.generate_form()

        if 'update' in self.request.POST:
            check_csrf_token(self.request)
            return self.process_form(form)

        return dict(user_name=self.user.get('name', 'Guest'),
                    title=self.panel_title(),
                    buttons=self.generate_buttons(),
                    userid=self.userid,
                    active=self.tab,
                    form=form.render(self.appstruct(), readonly=self.readonly()))
