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
    def nav_item(name, url, icon=None):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon)

    items = []
    if has_permission('edit', request.context, request):
        items.append( nav_item('Processes', request.route_path('processes_overview')) )
    if has_permission('submit', request.context, request):
        items.append( nav_item('My Jobs', request.route_path('myjobs_overview')) )
        items.append( nav_item('Wizard', request.route_path('wizard')) )
    items.append( nav_item('Help', request.route_url('readthedocs')) )
    
    subitems = []
    if has_permission('edit', request.context, request):
        subitems.append( nav_item('Profile', request.route_path('myaccount', tab='profile'), icon="glyphicon-user") )
        subitems.append( nav_item('Dashboard', request.route_path('dashboard', tab='jobs'), icon='glyphicon-dashboard') )
    if has_permission('admin', request.context, request):
        subitems.append( nav_item('Settings', request.route_path('settings'), icon="glyphicon-cog") )
    
    login = request.current_route_url() == request.route_url('account_login', protocol='esgf')

    return dict(title='Phoenix', items=items, subitems=subitems, username=authenticated_userid(request), login=login)

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

@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw)
             for name, args, kw in layout.headings])
    return ''



