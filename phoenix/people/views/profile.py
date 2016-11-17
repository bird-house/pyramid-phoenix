from pyramid.view import view_config, view_defaults
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from deform import Form, ValidationFailure, Button

from phoenix.views import MyView
from phoenix.utils import ActionButton
from ..schema import ProfileSchema, TwitcherSchema, ESGFCredentialsSchema, C4ISchema, GroupSchema

import logging
logger = logging.getLogger(__name__)


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
        elif self.tab == 'c4i':
            title = "C4I access token"
        elif self.tab == 'esgf':
            title = "ESGF access token"
        elif self.tab == 'group':
            title = 'Group permission'
        else:
            title = 'Profile'
        return title

    def appstruct(self):
        return self.collection.find_one({'identifier': self.userid})

    def schema(self):
        if self.tab == 'twitcher':
            schema = TwitcherSchema()
        elif self.tab == 'c4i':
            schema = C4ISchema()
        elif self.tab == 'esgf':
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
                        readonly=not self.request.has_permission('admin'),
                        formid='deform')
        elif self.tab == 'profile':
            btn = Button(name='update', title='Update Profile', css_class="btn btn-success btn-lg btn-block")
            form = Form(schema=self.schema(), buttons=(btn,), formid='deform')
        elif self.tab == 'c4i':
            btn = Button(name='update', title='Update C4I Token', css_class="btn btn-success btn-lg btn-block")
            form = Form(schema=self.schema(), buttons=(btn,), formid='deform')
        else:
            form = Form(schema=self.schema(), formid='deform')
        return form

    def generate_button(self):
        btn = None
        if self.tab == 'twitcher':
            btn = ActionButton(name='generate_twitcher_token', title='Generate Token',
                               css_class="btn btn-success btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href=self.request.route_path('generate_twitcher_token'))
        elif self.tab == 'c4i':
            btn = ActionButton(name='generate_c4i_token', title='Generate C4I Token',
                               css_class="btn btn-success btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href="https://dev.climate4impact.eu/impactportal/account/tokenapi.jsp")
        elif self.tab == 'esgf':
            btn = ActionButton(name='forget_esgf_certs', title='Forget ESGF credential',
                               css_class="btn btn-danger btn-xs",
                               disabled=not self.request.has_permission('submit'),
                               href=self.request.route_path('forget_esgf_certs'))
        return btn

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            for key in ['name', 'email', 'organisation', 'notes', 'group', 'c4i_token']:
                if key in appstruct:
                    self.user[key] = appstruct.get(key)
            self.collection.update({'identifier': self.userid}, self.user)
        except ValidationFailure, e:
            logger.exception('validation of form failed.')
            return dict(form=e.render())
        else:
            self.request.session.flash("Your profile was updated.", queue='success')
        return HTTPFound(location=self.request.current_route_path())

    @view_config(route_name='profile', renderer='../templates/people/profile.pt')
    def view(self):
        form = self.generate_form()

        if 'update' in self.request.POST:
            return self.process_form(form)

        return dict(user_name=self.user.get('name', 'Unknown'),
                    title=self.panel_title(),
                    button=self.generate_button(),
                    userid=self.userid,
                    active=self.tab,
                    form=form.render(self.appstruct()))
