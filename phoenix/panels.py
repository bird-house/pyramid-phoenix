from pyramid_layout.panel import panel_config
from pyramid.security import authenticated_userid, has_permission
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from deform import Form, ValidationFailure
from phoenix import models

import logging
logger = logging.getLogger(__name__)

# navbar
# ------
@panel_config(name='navbar', renderer='phoenix:templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active)

    nav = []
    if has_permission('edit', request.context, request):
        nav.append( nav_item('Dashboard', request.route_url('dashboard', tab='jobs')) )
        nav.append( nav_item('Processes', request.route_url('processes')) )
        nav.append( nav_item('My Jobs', request.route_url('myjobs')) )
        nav.append( nav_item('Wizard', request.route_url('wizard')) )
        # TODO: enable map again when it is working
        #nav.append( nav_item('Map', request.route_url('map')) )
        nav.append( nav_item('My Account', request.route_url('myaccount', tab='profile')) )
    if has_permission('admin', request.context, request):
        nav.append( nav_item('Settings', request.route_url('settings')) )
    nav.append( nav_item('Help', request.registry.settings.get('help.url')) )

    login = request.current_route_url() == request.route_url('signin', tab='esgf')

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request), login=login)

@panel_config(name='welcome', renderer='phoenix:templates/panels/welcome.pt')
def welcome(context, request, title):
    return dict(title=title, logged_in=authenticated_userid(request))

@panel_config(name='breadcrumbs', renderer='phoenix:templates/panels/breadcrumbs.pt')
def breadcrumbs(context, request):
    lm = request.layout_manager
    return dict(breadcrumbs=lm.layout.breadcrumbs)

@panel_config(name='sidebar', renderer='phoenix:templates/panels/sidebar.pt')
def sidebar(context, request):
    return dict()

@panel_config(name='footer', renderer='phoenix:templates/panels/footer.pt')
def footer(context, request):
    return {}

@panel_config(name='logon_openid', renderer='phoenix:templates/panels/logon_openid.pt')
def logon_openid(context, request):
    return {}

@panel_config(name='logon_esgf', renderer='phoenix:templates/panels/logon_esgf.pt')
def logon_esgf(context, request):
    return {}

@panel_config(name='dashboard_users', renderer='phoenix:templates/panels/dashboard_users.pt')
def dashboard_users(context, request):
    from phoenix.models import user_stats
    return user_stats(request)

@panel_config(name='dashboard_jobs', renderer='phoenix:templates/panels/dashboard_jobs.pt')
def dashboard_jobs(context, request):
    return dict(total = request.db.jobs.count(),
                started = request.db.jobs.find({"is_complete": False}).count(),
                failed = request.db.jobs.find({"is_complete": True, "is_succeded": False}).count(),
                succeded = request.db.jobs.find({"is_succeded": True}).count())

class MyAccoutProfile(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def generate_form(self):
        from phoenix.schema import UserProfileSchema
        form = Form(schema=UserProfileSchema(), buttons=('update',), formid='deform')
        return form
    
    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = models.get_user(self.request)
            for key in ['name', 'organisation', 'notes']:
                user[key] = appstruct.get(key)
            self.request.db.users.update({'email':models.user_email(self.request)}, user)
        except ValidationFailure, e:
            logger.exception('validation of form failed.')
            return dict(form=e.render())
        except Exception, e:
            logger.exception('update user failed.')
            self.request.session.flash('Update of your accound failed. %s' % (e), queue='error')
        else:
            self.request.session.flash("Your account was updated.", queue='success')
        #return HTTPFound(location=request.route_url('myaccount', tab='profile'))

    def appstruct(self):
        appstruct = models.get_user(self.request)
        if appstruct is None:
            appstruct = {}
        return appstruct

    @panel_config(name='myaccount_profile', renderer='phoenix:templates/panels/myaccount_default.pt')
    def panel(self):
        form = self.generate_form()
        if 'update' in self.request.POST:
            self.process_form(form)
        return dict(title="Profile", form=form.render( self.appstruct() ))

class MyAccountESGF(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def generate_form(self):
        from phoenix.schema import ESGFCredentialsSchema
        form = Form(schema=ESGFCredentialsSchema(), formid='deform')
        return form

    def appstruct(self):
        appstruct = models.get_user(self.request)
        if appstruct is None:
            appstruct = {}
        return appstruct

    @panel_config(name='myaccount_esgf', renderer='phoenix:templates/panels/myaccount_default.pt')
    def panel(self):
        form = self.generate_form()
        return dict(title="ESGF Access", form=form.render( self.appstruct() ))

class MyAccountSwift(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def generate_form(self):
        from phoenix.schema import SwiftSchema
        form = Form(schema=SwiftSchema(), formid='deform')
        return form

    def appstruct(self):
        appstruct = models.get_user(self.request)
        if appstruct is None:
            appstruct = {}
        return appstruct

    @panel_config(name='myaccount_swift', renderer='phoenix:templates/panels/myaccount_default.pt')
    def panel(self):
        form = self.generate_form()
        return dict(title="Swift Access", form=form.render( self.appstruct() ))

@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw)
             for name, args, kw in layout.headings])
    return ''



