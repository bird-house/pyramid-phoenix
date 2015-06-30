from pyramid_layout.panel import panel_config
from pyramid.security import authenticated_userid, has_permission
from phoenix.models import get_user

import logging
logger = logging.getLogger(__name__)


@panel_config(name='navbar', renderer='phoenix:templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url, icon=None):
        from phoenix.utils import root_path
        active = root_path(request.current_route_path()) == root_path(url)
        return dict(name=name, url=url, active=active, icon=icon)

    items = []
    if has_permission('edit', request.context, request):
        items.append( nav_item('Processes', request.route_path('processes')) )
    if has_permission('submit', request.context, request):
        items.append( nav_item('Wizard', request.route_path('wizard')) )
        items.append( nav_item('Monitor', request.route_path('monitor')) )
        
    subitems = []
    if has_permission('edit', request.context, request):
        subitems.append( nav_item('Profile', request.route_path('profile', tab='account'), icon="fa fa-user") )
        subitems.append( nav_item('Dashboard', request.route_path('dashboard', tab='jobs'), icon='fa fa-dashboard') )
    if has_permission('admin', request.context, request):
        subitems.append( nav_item('Settings', request.route_path('settings'), icon="fa fa-wrench") )
    
    login = 'login' in request.current_route_url()

    username = None
    try:
        user = get_user(request)
        if user:
            username = user.get('name')
    except:
        logger.exception('could not get username')

    return dict(title='Phoenix', items=items, subitems=subitems, username=username, login=login)


@panel_config(name='breadcrumbs', renderer='phoenix:templates/panels/breadcrumbs.pt')
def breadcrumbs(context, request):
    lm = request.layout_manager
    return dict(breadcrumbs=lm.layout.breadcrumbs)


@panel_config(name='sidebar', renderer='phoenix:templates/panels/sidebar.pt')
def sidebar(context, request):
    return dict()


@panel_config(name='footer', renderer='phoenix:templates/panels/footer.pt')
def footer(context, request):
    from phoenix import get_version
    return dict(version=get_version())


@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw)
             for name, args, kw in layout.headings])
    return ''



