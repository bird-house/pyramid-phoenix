from pyramid_layout.panel import panel_config
from pyramid.security import authenticated_userid, has_permission

import logging

log = logging.getLogger(__name__)

from .helpers import wps_url

# navbar
# ------
@panel_config(name='navbar',
              renderer='templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url, icon):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon)

    nav = []
    nav.append( nav_item('Home', request.route_url('home'), 'icon-home') )
    if has_permission('edit', request.context, request):
        nav.append( nav_item('Processes', request.route_url('processes'), 'icon-star') )
        nav.append( nav_item('My Jobs', request.route_url('jobs'), 'icon-list') )
        nav.append( nav_item('Wizard', request.route_url('wizard'), 'icon-star') )
        nav.append( nav_item('Map', request.route_url('map'), 'icon-picture') )
    if has_permission('admin', request.context, request):
        nav.append( nav_item('Thredds', request.route_url('tds'), 'icon-list') )
        nav.append( nav_item('Catalog', request.route_url('catalog_wps_select'), 'icon-edit') )
        nav.append( nav_item('Monitor', request.route_url('monitor'), 'icon-eye-open') )
        nav.append( nav_item('Admin', request.route_url('admin_user_edit'), 'icon-edit') )
    nav.append( nav_item('Help', request.route_url('help'), 'icon-question-sign') )

    login = request.current_route_url() == request.route_url('signin')

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request), login=login)

# catalog_navbar
# ------
@panel_config(name='catalog_navbar',
              renderer='templates/panels/subnavbar.pt')
def catalog_navbar(context, request):
    def nav_item(name, url, icon):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon)

    nav = [
        nav_item('Select WPS', request.route_url('catalog_wps_select'), 'icon-tasks'),
        nav_item('Add WPS', request.route_url('catalog_wps_add'), 'icon-tasks'),
        ]

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request))

# admin_navbar
# ------
@panel_config(name='admin_navbar',
              renderer='templates/panels/subnavbar.pt')
def admin_navbar(context, request):
    def nav_item(name, url, icon):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon)

    nav = [
        nav_item('Register User', request.route_url('admin_user_register'), 'icon-edit'),
        nav_item('Unregister Users', request.route_url('admin_user_unregister'), 'icon-edit'),
        nav_item('Activate Users', request.route_url('admin_user_activate'), 'icon-edit'),
        nav_item('Deactivate Users', request.route_url('admin_user_deactivate'), 'icon-edit'),
        nav_item('Edit User', request.route_url('admin_user_edit'), 'icon-edit'),
        ]

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request))


#==============================================================================
# user_statistic
#==============================================================================

# @panel_config(name='user_statistic',
#               renderer='templates/panels/user_statistic.pt')
# def user_statistic(context, request):
#     userid = authenticated_userid(request)
#     processes = []

#     if userid:
#         processes = ProcessHistory.status_count_by_userid(userid)

#     lastlogin = 'first login'
#     if 'lastlogin' in request.cookies:
#         lastlogin = request.cookies['lastlogin']

#     return dict(lastlogin=lastlogin, processes=processes)


#==============================================================================
# welcome
#==============================================================================

@panel_config(name='welcome',
              renderer='templates/panels/welcome.pt')
def welcome(context, request, title):
    return dict(title=title,
                logged_in=authenticated_userid(request),
                wps_service_url=wps_url(request))


#==============================================================================
# heading_processes
#==============================================================================

@panel_config(name='heading_processes',
              renderer='templates/panels/heading_processes.pt')
def heading_processes(context, request):
    return dict(title='Run a process')


#==============================================================================
# heading_history
#==============================================================================

@panel_config(name='heading_jobs',
              renderer='templates/panels/heading_jobs.pt')
def heading_history(context, request):
    return dict(title='Monitor processes')

#==============================================================================
# heading_demo
#==============================================================================

@panel_config(name='heading_info',
              renderer='templates/panels/heading_info.pt')
def heading_info(context, request):
    return dict(title='Info')

#==============================================================================
# heading_users
#==============================================================================

@panel_config(name='heading_stats',
              renderer='templates/panels/heading_stats.pt')
def heading_statistics(context, request):
    from .models import count_users
    return dict(title='Statistics', num_users=count_users(request))


#==============================================================================
# headings
#==============================================================================

@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw)
             for name, args, kw in layout.headings])
    return ''


#==============================================================================
# footer
#==============================================================================

@panel_config(name='footer')
def footer(context, request):
    return ''
    #return '<footer>&copy; </footer>'
    #return '<div class="well footer"><small>&copy; </small></div>'
