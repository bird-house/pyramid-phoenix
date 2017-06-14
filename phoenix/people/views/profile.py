from datetime import datetime

from pyramid.view import view_config, view_defaults
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from deform import Form, ValidationFailure, Button

from phoenix.views import MyView
from phoenix.utils import ActionButton
from phoenix.people.schema import (
    ProfileSchema,
    TwitcherSchema,
    ESGFSLCSTokenSchema,
    ESGFCredentialsSchema,
    GroupSchema
)

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
        if self.tab == 'twitcher':
            title = "Personal access token"
        elif self.tab == 'esgf_slcs':
            title = "ESGF SLCS access token"
        elif self.tab == 'esgf_certs':
            title = "ESGF X509 credentials"
        elif self.tab == 'group':
            title = 'Group permission'
        else:
            title = 'Profile'
        return title

    def appstruct(self):
        appstruct = self.collection.find_one({'identifier': self.userid})
        token = self.user.get('esgf_token')
        if token:
            appstruct['esgf_token'] = token.get('access_token')
            expires_at = datetime.utcfromtimestamp(
                int(token.get('expires_at'))).strftime(format="%Y-%m-%d %H:%M:%S UTC")
            appstruct['esgf_token_expires_at'] = expires_at
        token = self.user.get('twitcher_token')
        if token:
            appstruct['twitcher_token'] = token.get('access_token')
            expires_at = datetime.utcfromtimestamp(
                int(token.get('expires_at'))).strftime(format="%Y-%m-%d %H:%M:%S UTC")
            appstruct['twitcher_token_expires_at'] = expires_at
        return appstruct

    def readonly(self):
        if self.tab == 'group':
            return not self.request.has_permission('admin')
        else:
            return False

    def schema(self):
        if self.tab == 'twitcher':
            schema = TwitcherSchema()
        elif self.tab == 'esgf_slcs':
            schema = ESGFSLCSTokenSchema()
        elif self.tab == 'esgf_certs':
            schema = ESGFCredentialsSchema()
        elif self.tab == 'group':
            schema = GroupSchema()
        else:
            schema = ProfileSchema()
        return schema

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
        if self.tab == 'twitcher':
            btn = ActionButton(name='generate_twitcher_token', title='Generate Token',
                               css_class="btn btn-success btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href=self.request.route_path('generate_twitcher_token'))
            btns.append(btn)
        elif self.tab == 'esgf_slcs':
            btn = ActionButton(name='generate_esgf_slcs_token', title='Generate Token',
                               css_class="btn btn-success btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href=self.request.route_path('generate_esgf_slcs_token'))
            btns.append(btn)
            btn = ActionButton(name='forget_esgf_slcs_token', title='Forget Token',
                               css_class="btn btn-danger btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href=self.request.route_path('forget_esgf_slcs_token'))
            btns.append(btn)
        elif self.tab == 'esgf_certs':
            btn = ActionButton(name='update_esgf_certs', title='Update Credentials',
                               css_class="btn btn-success btn-xs",
                               disabled=not self.request.has_permission('edit'),
                               href=self.request.route_path('update_esgf_certs'))
            btns.append(btn)
            btn = ActionButton(name='forget_esgf_certs', title='Forget Credentials',
                               css_class="btn btn-danger btn-xs",
                               disabled=not self.request.has_permission('edit'),
                               href=self.request.route_path('forget_esgf_certs'))
            btns.append(btn)
        return btns

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            for key in ['name', 'email', 'organisation', 'notes', 'group']:
                if key in appstruct:
                    self.user[key] = appstruct.get(key)
            self.collection.update({'identifier': self.userid}, self.user)
        except ValidationFailure, e:
            LOGGER.exception('validation of form failed.')
            return dict(form=e.render())
        else:
            self.request.session.flash("Your profile was updated.", queue='success')
        return HTTPFound(location=self.request.current_route_path())

    @view_config(route_name='profile', renderer='../templates/people/profile.pt')
    def view(self):
        form = self.generate_form()

        if 'update' in self.request.POST:
            return self.process_form(form)

        return dict(user_name=self.user.get('name', 'Guest'),
                    title=self.panel_title(),
                    buttons=self.generate_buttons(),
                    userid=self.userid,
                    active=self.tab,
                    form=form.render(self.appstruct(), readonly=self.readonly()))
