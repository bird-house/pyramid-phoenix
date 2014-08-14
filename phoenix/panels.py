from pyramid_layout.panel import panel_config
from pyramid.security import authenticated_userid, has_permission

import logging
logger = logging.getLogger(__name__)

# navbar
# ------
@panel_config(name='navbar',
              renderer='phoenix:templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active)

    nav = []
    nav.append( nav_item('Dashboard', request.route_url('dashboard')) )
    if has_permission('edit', request.context, request):
        nav.append( nav_item('Processes', request.route_url('processes')) )
        nav.append( nav_item('My Jobs', request.route_url('myjobs')) )
        nav.append( nav_item('Wizard', request.route_url('wizard_wps')) )
        nav.append( nav_item('Map', request.route_url('map')) )
        nav.append( nav_item('My Account', request.route_url('myaccount')) )
    if has_permission('admin', request.context, request):
        nav.append( nav_item('Settings', request.route_url('all_settings')) )
    #nav.append( nav_item('Help', request.route_url('help')) )

    login = request.current_route_url() == request.route_url('signin')

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request), login=login)

@panel_config(name='welcome', renderer='phoenix:templates/panels/welcome.pt')
def welcome(context, request, title):
    return dict(title=title, logged_in=authenticated_userid(request))

@panel_config(name='sidebar', renderer='phoenix:templates/panels/sidebar.pt')
def sidebar(context, request):
    return dict(title="Sidebar...")

@panel_config(name='footer', renderer='phoenix:templates/panels/footer.pt')
def footer(context, request):
    return {}

@panel_config(name='dashboard_users',
              renderer='phoenix:templates/panels/dashboard_users.pt')
def heading_users(context, request):
    from .models import user_stats
    return user_stats(request)

@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw)
             for name, args, kw in layout.headings])
    return ''



