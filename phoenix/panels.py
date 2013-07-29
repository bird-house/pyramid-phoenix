from pyramid_layout.panel import panel_config
from pyramid.security import authenticated_userid

import logging

log = logging.getLogger(__name__)

from .models import ProcessHistory
from .helpers import wps_url

# navbar
# ------
@panel_config(name='navbar',
              renderer='templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url, icon):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon)

    nav = [nav_item('Home', request.route_url('home'), 'icon-home'),
           nav_item('Catalog', request.route_url('catalog_wps_select'), 'icon-tasks'),
           nav_item('Processes', request.route_url('processes'), 'icon-tasks'),
           nav_item('History', request.route_url('history'), 'icon-time'),
           nav_item('Monitor', request.route_url('monitor'), 'icon-time'),
           nav_item('Admin', request.route_url('admin'), 'icon-time'),
           nav_item('ESGF Search', request.route_url('esgsearch'), 'icon-time'),
           nav_item('Workflow', request.route_url('workflow'), 'icon-time'),
           nav_item('Help', request.route_url('help'), 'icon-time')]

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request))

# catalog_navbar
# ------
@panel_config(name='catalog_navbar',
              renderer='templates/panels/subnavbar.pt')
def catalog_navbar(context, request):
    def nav_item(name, url, icon):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon)

    nav = [nav_item('Select WPS', request.route_url('catalog_wps_select'), 'icon-tasks'),
           nav_item('Add WPS', request.route_url('catalog_wps_add'), 'icon-tasks'),
          ]

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request))


#==============================================================================
# user_statistic
#==============================================================================

@panel_config(name='user_statistic',
              renderer='templates/panels/user_statistic.pt')
def user_statistic(context, request):
    userid = authenticated_userid(request)
    processes = []

    if userid:
        processes = ProcessHistory.status_count_by_userid(userid)

    lastlogin = 'first login'
    if 'lastlogin' in request.cookies:
        lastlogin = request.cookies['lastlogin']

    return dict(lastlogin=lastlogin, processes=processes)


#==============================================================================
# welcome
#==============================================================================

@panel_config(name='welcome',
              renderer='templates/panels/welcome.pt')
def welcome(context, request, title):
    log.debug('rendering welcome panel')
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

@panel_config(name='heading_history',
              renderer='templates/panels/heading_history.pt')
def heading_history(context, request):
    return dict(title='Monitor processes')


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
