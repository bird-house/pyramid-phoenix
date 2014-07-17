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
    def nav_item(name, url, icon, dropdowns=[]):
        active = request.current_route_url() == url
        return dict(name=name, url=url, active=active, icon=icon, dropdowns=dropdowns)

    nav = []
    nav.append( nav_item('Home', request.route_url('home'), 'icon-home') )
    if has_permission('edit', request.context, request):
        nav.append( nav_item('Processes', request.route_url('processes'), 'icon-star') )
        nav.append( nav_item('My Jobs', request.route_url('jobs'), 'icon-list') )
        dropdowns = []
        dropdowns.append(nav_item('Simple', request.route_url('wizard'), 'icon-star'))
        dropdowns.append(nav_item('QC Full', request.route_url('qc_wizard_check'), 'icon-star'))
        dropdowns.append(nav_item('QC YAML', request.route_url('qc_wizard_yaml'), 'icon-star'))
        nav.append( nav_item('Wizard', None, 'icon-star', dropdowns) )
        nav.append( nav_item('Map', request.route_url('map'), 'icon-globe') )
        nav.append( nav_item('My Account', request.route_url('account'), 'icon-user') )
    if has_permission('admin', request.context, request):
        nav.append( nav_item('Settings', request.route_url('settings'), 'icon-edit') )
    nav.append( nav_item('Help', request.route_url('help'), 'icon-question-sign') )

    login = request.current_route_url() == request.route_url('signin')

    return dict(title='Phoenix', nav=nav, username=authenticated_userid(request), login=login)


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


@panel_config(name='welcome', renderer='templates/panels/welcome.pt')
def welcome(context, request, title):
    return dict(title=title,
                logged_in=authenticated_userid(request),
                wps_service_url=wps_url(request))

@panel_config(name='heading_processes', renderer='templates/panels/heading_processes.pt')
def heading_processes(context, request):
    return dict(title='Run a process')

@panel_config(name='heading_jobs',
              renderer='templates/panels/heading_jobs.pt')
def heading_history(context, request):
    return dict(title='Monitor processes')

@panel_config(name='heading_info',
              renderer='templates/panels/heading_info.pt')
def heading_info(context, request):
    return dict(title='Info')

@panel_config(name='heading_stats',
              renderer='templates/panels/heading_stats.pt')
def heading_statistics(context, request):
    import models
    userdb = models.User(request)
    return userdb.count()

@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw)
             for name, args, kw in layout.headings])
    return ''

@panel_config(name='footer')
def footer(context, request):
    return ''
    #return '<footer>&copy; </footer>'
    #return '<div class="well footer"><small>&copy; </small></div>'
