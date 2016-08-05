from pyramid_layout.panel import panel_config

from phoenix.security import auth_protocols

import logging
logger = logging.getLogger(__name__)


@panel_config(name='navbar', renderer='phoenix:templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url, icon=None):
        from phoenix.utils import root_path
        active = root_path(request.current_route_path()) == root_path(url)
        return dict(name=name, url=url, active=active, icon=icon)

    items = list()
    items.append( nav_item('Processes', request.route_path('processes')))
    if request.wizard_activated:
        items.append( nav_item('Wizard', request.route_path('wizard')))
    items.append( nav_item('Monitor', request.route_path('monitor')))
    items.append( nav_item('Map', request.route_path('map')))
        
    subitems = list()
    subitems.append( nav_item('Dashboard', request.route_path('dashboard', tab='overview'), icon='fa fa-dashboard'))
    if request.has_permission('admin'):
        subitems.append(nav_item('People', request.route_path('people'), icon="fa fa-users"))
        subitems.append( nav_item('Settings', request.route_path('settings'), icon="fa fa-wrench"))

    return dict(items=items, subitems=subitems, protocol=auth_protocols(request)[-1])


@panel_config(name='messages', renderer='phoenix:templates/panels/messages.pt')
def messages(context, request):
    return dict()


@panel_config(name='breadcrumbs', renderer='phoenix:templates/panels/breadcrumbs.pt')
def breadcrumbs(context, request):
    lm = request.layout_manager
    return dict(breadcrumbs=lm.layout.breadcrumbs)


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



