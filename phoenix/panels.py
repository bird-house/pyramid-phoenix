from pyramid_layout.panel import panel_config

from phoenix.security import default_auth_protocol
from phoenix.utils import root_path

import logging
logger = logging.getLogger(__name__)


@panel_config(name='navbar', renderer='phoenix:templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url, icon=None):
        active = root_path(request.current_route_path()) == root_path(url)
        return dict(name=name, url=url, active=active, icon=icon)

    def dropdown(name, items=None, icon=None):
        items = items or []
        return dict(name=name, icon=icon, items=items)

    items = list()
    items.append(nav_item('Processes', request.route_path('processes')))
    if request.has_permission('edit'):
        if request.wizard_activated:
            items.append(nav_item('Wizard', request.route_path('wizard')))
        items.append(nav_item('Monitor', request.route_path('monitor')))
        if request.map_activated:
            items.append(nav_item('Map', request.route_path('map')))

    subitems = list()
    subitems.append(nav_item('Dashboard', request.route_path('dashboard', tab='overview'), icon='fa fa-dashboard'))
    # dropdown browse
    browse_items = list()
    browse_items.append(nav_item('ESGF search', request.route_path('esgfsearch'), icon='fa fa-globe'))
    if request.solr_activated:
        browse_items.append(nav_item('Birdhouse Solr', request.route_path('solrsearch'), icon='fa fa-sun-o'))
    subitems.append(dropdown('Browse', items=browse_items, icon='fa fa-search'))
    if request.has_permission('submit'):
        subitems.append(nav_item('Cart', request.route_path('cart'), icon='fa fa-shopping-cart'))
    if request.has_permission('admin'):
        subitems.append(nav_item('People', request.route_path('people'), icon="fa fa-users"))
        subitems.append(nav_item('Supervisor', request.route_path('supervisor'), icon="fa fa-eye"))
        subitems.append(nav_item('Settings', request.route_path('settings'), icon="fa fa-wrench"))

    return dict(items=items, subitems=subitems, protocol=default_auth_protocol(request))


@panel_config(name='messages', renderer='phoenix:templates/panels/messages.pt')
def messages(context, request):
    return dict()


@panel_config(name='breadcrumbs', renderer='phoenix:templates/panels/breadcrumbs.pt')
def breadcrumbs(context, request):
    lm = request.layout_manager
    return dict(breadcrumbs=lm.layout.breadcrumbs)


@panel_config(name='footer', renderer='phoenix:templates/panels/footer.pt')
def footer(context, request):
    from phoenix import __version__ as version
    return dict(version=version)


@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw) for name, args, kw in layout.headings])
    return ''
